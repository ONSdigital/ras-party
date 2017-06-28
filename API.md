# Party Service API

### The implemented API for this serivce can be found at /swagger/party/party-api.yaml

### CAVEAT: This page is subject to change while the Party service is being developed.

### Please contact the RAS development team before committing to these endpoints.
  
This page documents the Party service API endpoints. All endpoints return an `HTTP 200 OK` status code except where noted otherwise.

* `GET /businesses/id/d826818e-179e-467b-9936-6a8603dc8b46/business-associations`
* `GET /businesses/ref/499000011335/business-associations`

&mdash; This returns a business object with an array of respondent associations,  each association with an array of survey enrolments the respondent has with that business.



### Example JSON Response
```json
{
  id: "d826818e-179e-467b-9936-6a8603dc8b46",
  sampleUnitRef: "499000011335",
  businessAssociations: [
    {
      partyId: "2fe21b48-2408-42f7-bc43-02a349383f2e",
      enrolments: [
        {
          surveyId: "7b71db36-443b-4720-a1e1-52f1679cd9d9",
          name: "BRES"
        },
        {
          surveyId: "b41219fd-3bcb-48fa-8c53-71bbf37baf73",
          name: "CPI"
        }
      ]
    },
    {
      partyId: "4ed02a0b-8341-41a5-9d6c-d8395cfde1b5",
      enrolments: [
        {
          surveyId: "7b71db36-443b-4720-a1e1-52f1679cd9d9",
          name: "BRES"
        }
      ]
    },
    {
      partyId: "71d8f310-cec8-44c9-8d89-4610bf8578f7"
    }
  ]
}
```

* `GET /respondents/id/2fe21b48-2408-42f7-bc43-02a349383f2e/business-associations`

&mdash; This returns a respondent object with an array of business associations, each association with an array of survey enrolments the respondent has with that business.

### Example JSON Response
```json
{
  id: "d826818e-179e-467b-9936-6a8603dc8b46",
  businessAssociations: [
    {
      partyId: "d826818e-179e-467b-9936-6a8603dc8b46",
      sampleUnitRef: "499000011335",
        enrolments: [
          {
            surveyId: "7b71db36-443b-4720-a1e1-52f1679cd9d9",
            name: "BRES"
          },
          {
            surveyId: "b41219fd-3bcb-48fa-8c53-71bbf37baf73",
            name: "CPI"
          }
         ]
      },
    {
      partyId: "d7d4fc21-1eaf-4e43-a89f-21ae7aa9e3f6",
      sampleUnitRef: "499000011335"
    }
  ]
}
```
