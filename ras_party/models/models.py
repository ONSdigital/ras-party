import datetime
import enum
import logging
import uuid

import structlog
from jsonschema import Draft4Validator
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, ForeignKeyConstraint, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from werkzeug.exceptions import NotFound

from ras_party.models import GUID
from ras_party.support.util import filter_falsey_values, partition_dict


Base = declarative_base()
logger = structlog.wrap_logger(logging.getLogger(__name__))


class Business(Base):
    __tablename__ = 'business'

    UNIT_TYPE = 'B'

    # TODO: consider using postgres uuid for uuid pkey
    party_uuid = Column(GUID, unique=True, primary_key=True)
    business_ref = Column(Text, unique=True)
    respondents = relationship('BusinessRespondent', back_populates='business')
    attributes = relationship('BusinessAttributes', backref='business',
                              order_by='desc(BusinessAttributes.created_on)', lazy='joined')
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def validate(json_packet, schema):
        """
        Validate the JSON packet against the supplied schema

        :param json_packet: The incoming JSON packet (typically via a POST)
        :param schema: the JSON schema to validate against
        :return: an error iterator if the packet is invalid, otherwise False
        """
        validator = Draft4Validator(schema)
        if not validator.is_valid(json_packet):
            return [str(e) for e in validator.iter_errors(json_packet)]

    @staticmethod
    def to_party(business_data):
        """
        The Business posting is now the same as the Party posting (FIXME: not exactly), except that the Business version
        has a flat structure and the party service has attributes in a dictionary item called 'attributes'.
        So for business postings, we just convert the incoming version into the Party version, then we can
        use the Party code to post the object.

        :param business_data: The raw data in dictionary form
        :return: The same data transformed to generic party format
        """

        party, attrs = partition_dict(business_data, ['sampleUnitRef', 'sampleUnitType', 'id', "sampleSummaryId"])
        party['attributes'] = attrs
        return party

    @staticmethod
    def from_party_dict(party):

        b = Business(party_uuid=party.get('id', uuid.uuid4()), business_ref=party['sampleUnitRef'])
        ba = BusinessAttributes(business_id=b.party_uuid, sample_summary_id=party['sampleSummaryId'])
        ba.attributes = party.get('attributes')
        Business._populate_name_and_trading_as(ba)

        b.attributes.append(ba)
        b.valid = True
        return b

    def add_versioned_attributes(self, party):
        ba = BusinessAttributes(business_id=self.party_uuid,
                                sample_summary_id=party['sampleSummaryId'])
        ba.attributes = party.get('attributes')
        self._populate_name_and_trading_as(ba)

        self.attributes.append(ba)

    @staticmethod
    def _populate_name_and_trading_as(ba):
        name = '{runame1} {runame2} {runame3}'.format(**ba.attributes)
        trading_as = '{tradstyle1} {tradstyle2} {tradstyle3}'.format(**ba.attributes)
        ba.attributes['name'] = ' '.join(name.split())
        ba.attributes['trading_as'] = ' '.join(trading_as.split())
        ba.name = name
        ba.trading_as = trading_as

    @staticmethod
    def _get_respondents_associations(respondents):
        associations = []
        for business_respondent in respondents:
            respondent_dict = {
                "partyId": business_respondent.respondent.party_uuid,
                "businessRespondentStatus": business_respondent.respondent.status.name
            }
            enrolments = business_respondent.enrolment
            respondent_dict['enrolments'] = []
            for enrolment in enrolments:
                enrolments_dict = {
                    "surveyId": enrolment.survey_id,
                    "enrolmentStatus": EnrolmentStatus(enrolment.status).name
                }
                respondent_dict['enrolments'].append(enrolments_dict)
            associations.append(respondent_dict)
        return associations

    def to_business_dict(self, collection_exercise_id=None):
        """
        Gets a dict that contains both summary data and collection exercise data.  The collection exercise data will be
        for either the specified one if supplied, or the most recent one if not supplied

        :param collection_exercise_id: A collection exercise uuid
        :return: A dict containing both the summary data and business attributes for the business
        :rtype: dict
        """
        d = self.to_business_summary_dict(collection_exercise_id)
        attributes = self._get_attributes_for_collection_exercise(collection_exercise_id)
        return dict(d, **attributes.attributes)

    def to_business_summary_dict(self, collection_exercise_id=None):
        attributes = self._get_attributes_for_collection_exercise(collection_exercise_id)
        d = {
            'id': self.party_uuid,
            'sampleUnitRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'sampleSummaryId': attributes.sample_summary_id,
            'name': attributes.attributes.get('name'),
            'trading_as': attributes.attributes.get('trading_as'),
            'associations': self._get_respondents_associations(self.respondents)
        }
        return d

    def to_party_dict(self):
        attributes = self._get_attributes_for_collection_exercise()
        return {
            'id': self.party_uuid,
            'sampleUnitRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'sampleSummaryId': attributes.sample_summary_id,
            'attributes': attributes.attributes,
            'name': attributes.attributes.get('name'),
            'trading_as': attributes.attributes.get('trading_as'),
            'associations': self._get_respondents_associations(self.respondents)
        }

    def to_post_response_dict(self):
        return {
            'id': self.party_uuid,
            'sampleUnitRef': self.business_ref,
            'sampleUnitType': self.UNIT_TYPE,
            'sampleSummaryId': self.attributes[-1].sample_summary_id,
            'attributes': self.attributes[-1].attributes,
            'name': self.attributes[-1].name,
            'trading_as': self.attributes[-1].trading_as,
            'associations': self._get_respondents_associations(self.respondents)
        }

    def _get_attributes_for_collection_exercise(self, collection_exercise_id=None):
        if collection_exercise_id:
            for attributes in self.attributes:
                if attributes.collection_exercise == collection_exercise_id:
                    return attributes

        try:
            return next((attributes for attributes in self.attributes if attributes.collection_exercise))
        except StopIteration:
            logger.error("No active attributes for business", reference=self.business_ref, status=404)
            raise NotFound("Business with reference does not have any active attributes.")


class BusinessAttributes(Base):
    __tablename__ = 'business_attributes'

    id = Column("id", Integer(), primary_key=True)
    business_id = Column(GUID, ForeignKey('business.party_uuid'))
    sample_summary_id = Column(Text)
    collection_exercise = Column(Text)
    attributes = Column(JSONB)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    name = Column(Text)   # New columns placed at end of list in case code uses positional rather than named references
    trading_as = Column(Text)
    Index('attributes_name_idx', name)
    Index('attributes_trading_as_idx', trading_as)
    Index('attributes_business_idx', business_id)
    Index('attributes_sample_summary_idx', sample_summary_id)
    Index('attributes_business_sample_idx', business_id, sample_summary_id)
    Index('attributes_collection_exercise_idx', collection_exercise)
    Index('attributes_created_on_idx', created_on)

    def to_dict(self):
        """
        Returns a dictionary representation of all the columns in this model.  This was implemented because
        the vars() built-in function returns ALL attributes of this object, including a `_sa_instance_state`
        field that we don't want.

        :return: A dict with all the columns and their values
        """
        return {
            'id': self.id,
            'business_id': str(self.business_id),
            'sample_summary_id': self.sample_summary_id,
            'collection_exercise': self.collection_exercise,
            'attributes': self.attributes,
            'created_on': self.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.name,
            'trading_as': self.trading_as
        }


class BusinessRespondentStatus(enum.IntEnum):
    ACTIVE = 0
    INACTIVE = 1
    SUSPENDED = 2
    ENDED = 3


class BusinessRespondent(Base):
    __tablename__ = 'business_respondent'

    business_id = Column(GUID, ForeignKey('business.party_uuid'), primary_key=True)
    respondent_id = Column(Integer, ForeignKey('respondent.id'), primary_key=True)
    status = Column('status', Enum(BusinessRespondentStatus), default=BusinessRespondentStatus.ACTIVE)
    effective_from = Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = Column(DateTime)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business = relationship('Business', back_populates='respondents', lazy='joined')
    respondent = relationship('Respondent', back_populates='businesses', lazy='joined')
    enrolment = relationship('Enrolment', back_populates='business_respondent')
    Index('business_respondent_idx', respondent_id)


class RespondentStatus(enum.IntEnum):
    CREATED = 0
    ACTIVE = 1
    SUSPENDED = 2


class PendingEnrolment(Base):
    __tablename__ = 'pending_enrolment'

    id = Column(Integer, primary_key=True)
    case_id = Column(GUID)
    respondent_id = Column(Integer, ForeignKey('respondent.id'))
    business_id = Column(GUID)
    survey_id = Column(GUID)

    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    respondent = relationship('Respondent')
    Index('pending_enrolment_case_idx', case_id)

    __table_args__ = (
        ForeignKeyConstraint(['respondent_id'],
                             ['respondent.id']),
    )


class Respondent(Base):
    __tablename__ = 'respondent'

    UNIT_TYPE = 'BI'

    id = Column(Integer, primary_key=True)
    businesses = relationship('BusinessRespondent', back_populates='respondent')
    party_uuid = Column(GUID, unique=True)
    status = Column('status', Enum(RespondentStatus), default=RespondentStatus.CREATED)
    email_address = Column(Text, unique=True)
    pending_email_address = Column(Text, unique=True)
    first_name = Column(Text)
    last_name = Column(Text)
    telephone = Column(Text)
    mark_for_deletion = Column(Boolean, default=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    pending_enrolment = relationship('PendingEnrolment', back_populates='respondent')
    Index('respondent_first_name_idx', first_name)
    Index('respondent_last_name_idx', last_name)
    Index('respondent_email_idx', email_address)

    @staticmethod
    def _get_business_associations(businesses):
        associations = []
        for business_respondent in businesses:
            business_dict = {
                "partyId": business_respondent.business.party_uuid,
                "sampleUnitRef": business_respondent.business.business_ref,
                "businessRespondentStatus": business_respondent.respondent.status.name
            }
            enrolments = business_respondent.enrolment
            business_dict['enrolments'] = []
            for enrolment in enrolments:
                enrolments_dict = {
                    "surveyId": enrolment.survey_id,
                    "enrolmentStatus": EnrolmentStatus(enrolment.status).name
                }
                business_dict['enrolments'].append(enrolments_dict)
            associations.append(business_dict)
        return associations

    def to_respondent_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'pendingEmailAddress': self.pending_email_address,
            'emailAddress': self.email_address,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'telephone': self.telephone,
            'status': RespondentStatus(self.status).name,
            'markForDeletion': self.mark_for_deletion,
            'associations': self._get_business_associations(self.businesses)
        }

        return filter_falsey_values(d)

    def to_party_dict(self):
        d = {
            'id': self.party_uuid,
            'sampleUnitType': self.UNIT_TYPE,
            'status': RespondentStatus(self.status).name,
            'attributes': filter_falsey_values({
                'emailAddress': self.email_address,
                'firstName': self.first_name,
                'lastName': self.last_name,
                'telephone': self.telephone}),
            'associations': self._get_business_associations(self.businesses)
        }

        return d


class EnrolmentStatus(enum.IntEnum):
    PENDING = 0
    ENABLED = 1
    DISABLED = 2
    SUSPENDED = 3


class Enrolment(Base):
    __tablename__ = 'enrolment'

    business_id = Column(GUID, primary_key=True)
    respondent_id = Column(Integer, primary_key=True)
    survey_id = Column(Text, primary_key=True)
    status = Column('status', Enum(EnrolmentStatus), default=EnrolmentStatus.PENDING)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)

    business_respondent = relationship('BusinessRespondent', back_populates='enrolment', lazy='joined')
    Index('enrolment_business_idx', business_id)
    Index('enrolment_respondent_idx', respondent_id)
    Index('enrolment_survey_idx', survey_id)
    Index('enrolment_status_idx', status)

    __table_args__ = (
        ForeignKeyConstraint(['business_id', 'respondent_id'],
                             ['business_respondent.business_id', 'business_respondent.respondent_id']),
    )
