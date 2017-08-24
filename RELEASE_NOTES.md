Party Service Server
============================

Author: Nicholas Herriot
Version: 0.1.1

Changes For ras-party-service Server
============================================

* The info endpoint is using Flask Blueprints - no visible change.
* Errors are delt with in the ras_common_util library.

 
Known Issues For Party Service Server
============================================
* No roll back when creating a new user and a failure occurs on the OAuth2 server.
