#!/usr/bin/env python3
##############################################################################
#                                                                            #
#   Microservices header template                                            #
#   Date:    18 May 2017                                                     #
#   Author:  Gareth Bult                                                     #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from connexion import App
from flask_cors import CORS

from swagger_server.configuration import ons_env

if __name__ == '__main__':
    ons_env.activate()
    app = App(__name__, specification_dir='./swagger/')
    CORS(app.app)
    app.add_api('swagger.yaml', arguments={'title': 'ONS Microservice'})
    app.run(host='0.0.0.0', port=ons_env.port, debug=ons_env.debug)

    #from twisted.internet import reactor
    #from flask_twisted import Twisted
    #reactor.callLater(1, print, '<<Twisted is running>>')
    #Twisted(app).run(port=getenv('PORT',8080))