export VCAP_CRAP='HOLLY SHIT'

export VCAP_SERVICES='{
  "rds": [
   {
    "credentials": {
     "db_name": "my_demo_database",
     "host": "my_long_host_name.rds.amazonaws.com",
     "password": "my_secret_password",
#    "uri":"sqlite:///ras-party",
	 "uri": "postgresql://postgres:postgres@localhost:5431",
     "username": "my_long_hostname"
    },
    "label": "rds",
    "name": "ras-ps-db",
    "plan": "shared-psql",
    "provider": null,
    "syslog_drain_url": null,
    "tags": [
     "database",
     "RDS",
     "postgresql"
    ],
    "volume_mounts": []
   }
  ]
 }'


export VCAP_APPLICATION='{
  "application_id": "00000000-0000-0000-0000-000000000000",
  "application_name": "ras-collection-instrument-demo",
  "application_uris": [
   "ras-collection-instrument-demo.apps.devtest.onsclofo.uk"
  ],
  "application_version": "00000000-0000-0000-0000-000000000000",
  "cf_api": "https://api.system.devtest.onsclofo.uk",
  "limits": {
   "disk": 1024,
   "fds": 16384,
   "mem": 512
  },
  "name": "ras-collection-instrument-demo",
  "space_id": "000000000-0000-0000-0000-000000000000",
  "space_name": "demo",
  "uris": [
   "ras-collection-instrument-demo.apps.devtest.onsclofo.uk"
  ],
  "users": null,
  "version": "00000000-0000-0000-0000-000000000000"
 }'
