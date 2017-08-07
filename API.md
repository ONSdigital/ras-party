# Party Service API

### The implemented API for this serivce can be found at /swagger/party/party-api.yaml

### CAVEAT: This page is subject to change while the Party service is being developed.

### Please contact the RAS development team before committing to these endpoints.
  
This page documents the Party service API endpoints. All endpoints return an `HTTP 200 OK` status code except where noted otherwise.

* `GET /parties/type/B/ref/499000011335`
* `GET /parties/type/B/id/d826818e-179e-467b-9936-6a8603dc8b46`

&mdash; When generic party type 'B' (business) is requested this returns a generic party representation of the business resource. This representation will include any respondents associated with the business and any survey enrolments they have.

### Example JSON Response
```json
{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "name": "Business Register and Employment Survey",
                "surveyId: "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
            }
        ],
        "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233"
        }
    ],
    "attributes": {
        "contactName": "Bob Fish",
        "employeeCount": 50,
        "enterpriseName": "ACME Limited",
        "facsimile": "+44 1234 567890",
        "fulltimeCount": 35,
        "legalStatus": "Private Limited Company",
        "name": "ACME Ltd",
        "sic2003": "2520",
        "sic2007": "2520",
        "telephone": "+44 1234 567890",
        "tradingName": "ACME Trading Ltd",
        "turnover": 350
    },
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B"
}
```

* `GET /businesses/id/d826818e-179e-467b-9936-6a8603dc8b46`

&mdash; When a business is requested this returns a concrete representation of the business party.  This representation will include any respondents associated with the business and any survey enrolments they have.

### Example JSON Response

```json
{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "name": "Business Register and Employment Survey",
                "surveyId: "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
            }
        ],
        "partyId: "cd592e0f-8d07-407b-b75d-e01fbdae8233"
        }
    ],
    "attributes": { },
    "contactName": "Bob Fish",
    "employeeCount": 50,
    "enterpriseName": "ACME Limited",
    "facsimile": "+44 1234 567890",
    "fulltimeCount": 35,
    "legalStatus": "Private Limited Company",
    "name": "ACME Ltd",
    "sic2003": "2520",
    "sic2007": "2520",
    "telephone": "+44 1234 567890",
    "tradingName": "ACME Trading Ltd",
    "turnover": 350,
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B"
}
```


* `GET /parties/type/BI/id/3b136c4b-7a14-4904-9e01-13364dd7b972`

&mdash; When generic party type 'BI' (respondent) is requested this returns a generic party representation of the respondent resource. This representation will include any businesses associated with the respondent and any survey enrolments they have.

### Example JSON Response
```json
{
    "associations": [
        {
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "name": "Business Register and Employment Survey",
                    "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                }
            ],
            "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
            "sampleUnitRef": "50012345678"
        }
    ],
    "attributes": {
        "emailAddress": "Jacky.Turner@email.com",
        "firstName": "Jacky",
        "lastName": "Turner",
        "telephone": "7971161859"
    },
    "id": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
    "sampleUnitType": "BI",
    "status": "ACTIVE"
}
```

* `GET /respondents/id/3b136c4b-7a14-4904-9e01-13364dd7b972`

&mdash; When a respondent is requested this returns a concrete representation of the respondent party. This representation will include any businesses associated with the respondent and any survey enrolments they have.

### Example JSON Response
```json
{
    "associations": [
        {
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "name": "Business Register and Employment Survey",
                    "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
                }
            ],
            "partyId": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
            "sampleUnitRef": "50012345678"
        }
    ],
    "emailAddress": "Jacky.Turner@email.com",
    "firstName": "Jacky",
    "lastName": "Turner",
    "telephone": "7971161859",
    "id": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
    "sampleUnitType": "BI",
    "status": "ACTIVE"
}
```
