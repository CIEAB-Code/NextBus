# NextBus
Welcome to NextBus!
This is a simple Python3.8 web application using TFL (Transport for London) API that retrieves the latest bus arrival times and stores to a database. 

# Dependencies
-MongoDb-
A current version of MongoDb is required to run a local database for this app.
The version used here is 4.4.3.
Please see the the installation guide below.

-Python Requirements-
  -pymongo
  -flask
  -requests
  -json
  -datetime

# Installation
-MongoDb-
  1. Download MongoDB community version from https://mongodb.com/try/download/community.
  2. Follow installation wizard to install to system.
  3. Open the commandline in the MongoDB installation directory.
  4. At the commandline run: mongod.exe --dbpath (database directory path)
  5. Check running instance of MongoDB by navigating to http://localhost:27017

-Python Requirements-
  1. pip install (required modules)

-NextBus-
  1. git clone https://github.com/CIEAB-Code/NextBus.git
  2. unpack folder
  3. At the commandline run: python nextbus.py
  
# Buglist/Issue Fixes
- Fixed issue with empty table after midnight when there are no buses present, table now shows an error.

# features to add
- Add a query system for the historical DB table.
- Add a requirements.txt file for easier dependency installation.

