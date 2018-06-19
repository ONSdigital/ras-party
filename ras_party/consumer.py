import logging
import time

import pika
from structlog import wrap_logger
from sdc.rabbit.consumers import AsyncConsumer
from sdc.rabbit.exceptions import QuarantinableError, BadMessageError, PublishMessageError, RetryableError

logger = logging.getLogger(__name__)
logger = wrap_logger(logger)


class AsyncIOConsumer(AsyncConsumer):
    def connect(self):
        """This method connects to RabbitMQ using a TornadoConnection object,
        returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        count = 1
        no_of_servers = len(self._rabbit_urls)

        while True:
            server_choice = (count % no_of_servers) - 1

            self._url = self._rabbit_urls[server_choice]

            try:
                logger.info('Connecting')
                return pika.adapters.AsyncioConnection(pika.URLParameters(self._url),
                                                       self.on_connection_open,
                                                       stop_ioloop_on_close=False)
            except pika.exceptions.AMQPConnectionError as e:
                logger.exception("Connection error")
                count += 1
                logger.error("Connection sleep", no_of_seconds=count)
                time.sleep(count)

                continue


class MessageConsumer(AsyncIOConsumer):
    """This is a queue consumer that handles messages from RabbitMQ message queues.
    On receipt of a message it takes a number of params from the message
    properties, processes the message, and (if successful) positively
    acknowledges the publishing queue.
    If a message is not successfuly processed, it can be either negatively
    acknowledged, rejected or quarantined, depending on the type of excpetion
    raised.
    """

    @staticmethod
    def tx_id(properties):
        """
        Gets the tx_id for a message from a rabbit queue, using the
        message properties. Will raise KeyError if tx_id is missing from message
        headers.
        : param properties: Message properties
        : returns: tx_id of survey response
        : rtype: str
        """
        tx_id = properties.headers['tx_id']
        logger.info("Retrieved tx_id from message properties: tx_id={}".format(tx_id))
        return tx_id

    def __init__(self,
                 durable_queue,
                 exchange,
                 exchange_type,
                 rabbit_queue,
                 rabbit_urls,
                 quarantine_publisher,
                 process,
                 check_tx_id=True):
        """Create a new instance of the SDXConsumer class
        : param durable_queue: Boolean specifying whether queue is durable
        : param exchange: RabbitMQ exchange name
        : param exchange_type: RabbitMQ exchange type
        : param rabbit_queue: RabbitMQ queue name
        : param rabbit_urls: List of rabbit urls
        : param quarantine_publisher: Object of type sdc.rabbit.QueuePublisher.
            Will publish quarantined messages to the named queue.
        : param process: Function or method to use for processsing message. Will
            be passed the body of the message as a string decoded using UTF - 8.
            Should raise sdc.rabbit.DecryptError, sdc.rabbit.BadMessageError or
            sdc.rabbit.RetryableError on failure, depending on the failure mode.
        : returns: Object of type SDXConsumer
        : rtype: SDXConsumer
        """
        self.process = process
        if not callable(process):
            msg = 'process callback is not callable'
            raise AttributeError(msg.format(process))

        self.quarantine_publisher = quarantine_publisher
        self.check_tx_id = check_tx_id

        super().__init__(durable_queue,
                         exchange,
                         exchange_type,
                         rabbit_queue,
                         rabbit_urls)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Called on receipt of a message from a queue.
        Processes the message using the self._process method or function and positively
        acknowledges the queue if successful. If processing is not succesful,
        the message can either be rejected, quarantined or negatively acknowledged,
        depending on the failure mode.
        : param basic_deliver: AMQP basic.deliver method
        : param properties: Message properties
        : param body: Message body
        : returns: None
        """
        if self.check_tx_id:
            try:
                tx_id = self.tx_id(properties)

                logger.info('Received message',
                            queue=self._queue,
                            delivery_tag=basic_deliver.delivery_tag,
                            app_id=properties.app_id,
                            tx_id=tx_id)

            except KeyError as e:
                self.reject_message(basic_deliver.delivery_tag)
                logger.error("Bad message properties - no tx_id",
                             action="rejected",
                             exception=str(e))
                return None
            except TypeError as e:
                self.reject_message(basic_deliver.delivery_tag)
                logger.error("Bad message properties - no headers",
                             action="rejected",
                             exception=str(e))
                return None
        else:
            logger.debug("check_tx_id is False. Not checking tx_id for message.",
                         delivery_tag=basic_deliver.delivery_tag)
            tx_id = None

        try:
            try:
                self.process(body.decode("utf-8"), tx_id)
            except TypeError:
                logger.error('Incorrect call to process method')
                raise QuarantinableError

            self.acknowledge_message(basic_deliver.delivery_tag,
                                     tx_id=tx_id)

        except (QuarantinableError, BadMessageError) as e:
            # Throw it into the quarantine queue to be dealt with
            try:
                self.quarantine_publisher.publish_message(body, headers={'tx_id': tx_id})
                self.reject_message(basic_deliver.delivery_tag, tx_id=tx_id)
                logger.error("Quarantinable error occured",
                             action="quarantined",
                             exception=str(e),
                             tx_id=tx_id)
            except PublishMessageError as e:
                logger.error("Unable to publish message to quarantine queue." +
                             " Rejecting message and requeing.")
                self.reject_message(basic_deliver.delivery_tag,
                                    requeue=True,
                                    tx_id=tx_id)

        except RetryableError as e:
            self.nack_message(basic_deliver.delivery_tag, tx_id=tx_id)
            logger.error("Failed to process",
                         action="nack",
                         exception=str(e),
                         tx_id=tx_id)

        except Exception as e:
            self.nack_message(basic_deliver.delivery_tag, tx_id=tx_id)
            logger.exception("Unexpected exception occurred")
            logger.error("Failed to process",
                         action="nack",
                         exception=str(e),
                         tx_id=tx_id)