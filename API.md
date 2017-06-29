# Party Service API

### The implemented API for this serivce can be found at /swagger/party/party-api.yaml

### CAVEAT: This page is subject to change while the Party service is being developed.

### Please contact the RAS development team before committing to these endpoints.
  
This page documents the Party service API endpoints. All endpoints return an `HTTP 200 OK` status code except where noted otherwise.

* `GET /parties/type/B/ref/499000011335`
* `GET /parties/type/B/id/d826818e-179e-467b-9936-6a8603dc8b46`

&mdash; When generic party type 'B' (business) is requested this returns a generic party representation of the business resource. TODO: This representation will include any respondents associated with the business and any survey enrolments they have.

### Example JSON Response
```json
{
  "attributes": 
  {
    "contactName": "John Doe",
    "employeeCount": 50,
    "enterpriseName": "ABC Limited",
    "facsimile": "+44 1234 567890",
    "fulltimeCount": 35,
    "legalStatus": "Private Limited Company",
    "name": "Bolts and Ratchets Ltd",
    "sic2003": "2520",
    "sic2007": "2520",
    "telephone": "+44 1234 567890",
    "tradingName": "ABC Trading Ltd",
    "turnover": 350
  },
  "id": "d826818e-179e-467b-9936-6a8603dc8b46",
  "sampleUnitRef": "499000011335",
  "sampleUnitType": "B",
  "associations": [
    {
      "partyId": "3b136c4b-7a14-4904-9e01-13364dd7b972",
      "enrolments": [
        {
          "surveyId": "7b71db36-443b-4720-a1e1-52f1679cd9d9",
          "name": "BRES"
        },
        {
          "surveyId": "b41219fd-3bcb-48fa-8c53-71bbf37baf73",
          "name": "CPI"
        }
      ]
    },
    {
      "partyId": "4ed02a0b-8341-41a5-9d6c-d8395cfde1b5",
      "enrolments": [
        {
          "surveyId": "7b71db36-443b-4720-a1e1-52f1679cd9d9",
          "name": "BRES"
        }
      ]
    },
    {
      "partyId": "71d8f310-cec8-44c9-8d89-4610bf8578f7"
    }
  ]
}
```

* `GET /businesses/id/d826818e-179e-467b-9936-6a8603dc8b46`

&mdash; When a business is requested this returns a concrete representation of the business party. TODO: This representation will include any respondents associated with the business and any survey enrolments they have.

### Example JSON Response

```json
{
  "attributes": { },
  "businessRef": "499000011335",
  "contactName": "John Doe",
  "employeeCount": 50,
  "enterpriseName": "ABC Limited",
  "facsimile": "+44 1234 567890",
  "fulltimeCount": 35,
  "id": "d826818e-179e-467b-9936-6a8603dc8b46",
  "legalStatus": "Private Limited Company",
  "name": "Bolts and Ratchets Ltd",
  "sampleUnitType": "B",
  "sic2003": "2520",
  "sic2007": "2520",
  "telephone": "+44 1234 567890",
  "tradingName": "ABC Trading Ltd",
  "turnover": 350,
  "associations": [
    {
      "partyId": "3b136c4b-7a14-4904-9e01-13364dd7b972",
      "enrolments": [
        {
          "surveyId": "7b71db36-443b-4720-a1e1-52f1679cd9d9",
          "name": "BRES"
        },
        {
          "surveyId": "b41219fd-3bcb-48fa-8c53-71bbf37baf73",
          "name": "CPI"
        }
      ]
    },
    {
      "partyId": "4ed02a0b-8341-41a5-9d6c-d8395cfde1b5",
      "enrolments": [
        {
          "surveyId": "7b71db36-443b-4720-a1e1-52f1679cd9d9",
          "name": "BRES"
        }
      ]
    },
    {
      "partyId": "71d8f310-cec8-44c9-8d89-4610bf8578f7"
    }
  ]
}
```


* `GET /parties/type/BI/id/3b136c4b-7a14-4904-9e01-13364dd7b972`

&mdash; When generic party type 'BI' (respondent) is requested this returns a generic party representation of the respondent resource. TODO: This representation will include any businesses associated with the respondent and any survey enrolments they have.

### Example JSON Response
```json
{
  "attributes": {
    "emailAddress": "Jacky.Turner@abc-ltd.com",
    "firstName": "Jacky",
    "lastName": "Turner",
    "telephone": "+44 1234 567890"
  },
  "id": "3b136c4b-7a14-4904-9e01-13364dd7b972",
  "sampleUnitType": "BI",
  "associations": [
    {
      "partyId": "d826818e-179e-467b-9936-6a8603dc8b46",
      "sampleUnitRef": "499000011335",
        "enrolments": [
          {
            "surveyId": "7b71db36-443b-4720-a1e1-52f1679cd9d9",
            "name": "BRES"
          },
          {
            "surveyId": "b41219fd-3bcb-48fa-8c53-71bbf37baf73",
            "name": "CPI"
          }
         ]
      },
    {
      "partyId": "d7d4fc21-1eaf-4e43-a89f-21ae7aa9e3f6",
      "sampleUnitRef": "499000011335"
    }
  ]
}
```

* `GET /respondents/id/3b136c4b-7a14-4904-9e01-13364dd7b972`

&mdash; When a respondent is requested this returns a concrete representation of the respondent party. TODO: This representation will include any businesses associated with the respondent and any survey enrolments they have.

### Example JSON Response
```json
{
  "emailAddress": "Jacky.Turner@abc-ltd.com",
  "firstName": "Jacky",
  "id": "3b136c4b-7a14-4904-9e01-13364dd7b972",
  "lastName": "Turner",
  "sampleUnitType": "BI",
  "telephone": "+44 1234 567890",
  "associations": [
    {
      "partyId": "d826818e-179e-467b-9936-6a8603dc8b46",
      "sampleUnitRef": "499000011335",
        "enrolments": [
          {
            "surveyId": "7b71db36-443b-4720-a1e1-52f1679cd9d9",
            "name": "BRES"
          },
          {
            "surveyId": "b41219fd-3bcb-48fa-8c53-71bbf37baf73",
            "name": "CPI"
          }
         ]
      },
    {
      "partyId": "d7d4fc21-1eaf-4e43-a89f-21ae7aa9e3f6",
      "sampleUnitRef": "499000011335"
    }
  ]
}
```