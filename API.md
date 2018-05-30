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
                "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
            }
        ],
        "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "attributes": {
        "ruref": "50012345678",
        "checkletter": "A",
        "frosic92": "11111",
        "rusic92": "11111",
        "frosic2007": "11111",
        "rusic2007": "11111",
        "froempment": 50,    
        "frotover": 50,
        "entref": "1234567890",
        "legalstatus": "B",
        "entrepmkr": "C",
        "region": "DE",
        "birthdate": "01/09/1993",
        "entname1": "ENTNAME1",
        "entname2": "ENTNAME2",
        "entname3": "ENTNAME3",
        "runame1": "Bolts",
        "runame2": "and",
        "runame3": "Ratchets Ltd",
        "tradstyle1": "TRADSTYLE1",
        "tradstyle2": "TRADSTYLE2",
        "tradstyle3": "TRADSTYLE3",
        "seltype": "F",
        "inclexcl": "G",
        "cell_no": 1,     
        "formtype": "0001",
        "currency": "H",
    },
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B",
    "name": "Bolts and Ratchets Ltd"
}
```

* `GET /businesses/id/d826818e-179e-467b-9936-6a8603dc8b46`

&mdash; When a business is requested this returns a concrete representation of the business party. This representation will include any respondents associated with the business and any survey enrolments they have.

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
        "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "name": "Bolts and Ratchets Ltd",
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B"
}
```

*  Using verbose parameter: `GET /businesses/id/d826818e-179e-467b-9936-6a8603dc8b46?verbose=true`

&mdash; Verbose concrete representation of the business party.

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
        "businessRespondentStatus": "ACTIVE",
        "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233"
        }
    ],
    "ruref": "50012345678",
    "checkletter": "A",
    "frosic92": "11111",
    "rusic92": "11111",
    "frosic2007": "11111",
    "rusic2007": "11111",
    "froempment": 50,
    "frotover": 50,
    "entref": "1234567890",
    "legalstatus": "B",
    "entrepmkr": "C",
    "region": "DE",
    "birthdate": "01/09/1993",
    "entname1": "ENTNAME1",
    "entname2": "ENTNAME2",
    "entname3": "ENTNAME3",
    "runame1": "Bolts",
    "runame2": "and",
    "runame3": "Ratchets Ltd",
    "tradstyle1": "TRADSTYLE1",
    "tradstyle2": "TRADSTYLE2",
    "tradstyle3": "TRADSTYLE3",
    "seltype": "F",
    "inclexcl": "G",
    "cell_no": 1,
    "formtype": "0001",
    "currency": "H",
    "name": "Bolts and Ratchets Ltd",
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B"
}
```

* `GET /businesses?id=d826818e-179e-467b-9936-6a8603dc8b46&id=623435fa-708e-49c0-8f90-507ac862a540`

&mdash; When multiple businesses are requested this returns a concrete representation of the business parties. This representation will include any respondents associated with the business and any survey enrolments they have.

### Example JSON Response

```json
[{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "name": "Business Register and Employment Survey",
                "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
            }
        ],
        "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "name": "Bolts and Ratchets Ltd",
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B"
},
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
        "partyId": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "name": "Example Ltd",
    "id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sampleUnitRef": "50012345678",
    "sampleUnitType": "B"
}]
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
            "businessRespondentStatus": "ACTIVE",
            "sampleUnitRef": "50012345678"
        }
    ],
    "attributes": {
        "pendingEmailAddress": "J.Turner@email.com",
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

The pendingEmailAddress field holds the unverified email address when it is being updated.

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
            "businessRespondentStatus": "ACTIVE",
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

* `GET /respondents?id=3b136c4b-7a14-4904-9e01-13364dd7b972&id=be3711f4-d6c3-45e4-810e-5589b547cc5d`

&mdash; When multiple respondents are requested this returns a concrete representation of the respondent parties. This representation will include any businesses associated with the respondent and any survey enrolments they have.

### Example JSON Response
```json
[{
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
            "businessRespondentStatus": "ACTIVE",
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
},
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
            "businessRespondentStatus": "ACTIVE",
            "sampleUnitRef": "50012345678"
        }
    ],
    "emailAddress": "Timmy.Turner@email.com",
    "firstName": "Timmy",
    "lastName": "Turner",
    "telephone": "7971161859",
    "id": "cd592e0f-8d07-407b-b75d-e01fbdae8233",
    "sampleUnitType": "BI",
    "status": "ACTIVE"
}
]
```

* `PUT /respondents/email`
### Example JSON DATA for the put
```json
{
   "email_address": "old@email.com",
   "new_email_address": "new@email.com"
}
```
&mdash; This endpoint will update a respondent's email in the ras-party database and the oauth2 server. This email will need verified again so it will also set the user as unverified in the oauth server and will send a new verification email to the respondent.

### Example JSON Response
```json
{
   "emailAddress": "testtest@test.test",
   "firstName": "Test",
   "id": "ef7737df-2097-4a73-a530-e98dba7bfe43",
   "lastName": "tseT",
   "sampleUnitType": "BI",
   "status": "ACTIVE",
   "telephone": "07846608000"
}
```

* `PUT /businesses/sample/link/<sampleSummaryId>`
### Example JSON DATA for the put
```json
{
   "collectionExerciseId": "aCollectionExerciseId"
}
```
&mdash; This endpoint will update all businesses' attributes associated collection exercise id for given sample.

### Example JSON Response
```json
{
    "collectionExerciseId": "aCollectionExerciseId",
    "sampleSummaryId": "aSampleSummaryId"
}
```

* `POST /respondents/add-survey`

### Example JSON data for post
```json
{
    "party_id": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
    "enrolment_code": "fb747cq725lj"
}
```
&mdash; This endpoint will enrol a respondent in a survey and associate with business if not already associated.


* `PUT /respondents/edit-account-status/<respondent_party_id>`

### Example JSON data for put
```json
{
    "status_change": "SUSPENDED"
}
```
&mdash; This endpoint will change a respondent's account status based on status_change variable.


* `PUT /respondents/change_respondent_details/<respondent_id>`

### Example JSON data for put
```json
{
     " party_id": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
     "firstName": "John",
     "lastName": "Snow",
     "telephone": "07837230942"
}
```
&mdash; This endpoint will update the respondent details for an existing respondent.

