###Party Service API

######*Acceptance tests can be run to populate a local version with test data.*
<hr>

####Business Endpoints:

* `POST /businesses`
    * Must be provided all data outside of the `attributes` field, as well as `runame1`, `runame2` and `runname3` from within `attributes`, other fields are not required.
    * Must be prefaced with `/party-api/v1/` in url string (or current version).

#####Example JSON Response (jsonify'd)
```json
{
{
  "associations": [
    
  ],
  "attributes": {
     "birthdate": "1/1/2001",
     "cell_no": 1,
      "checkletter": "A",
      "currency": "S",
      "entname1": "Ent-1",
      "entname2": "Ent-2",
      "entname3": "Ent-3",
      "entref": "Entref",
      "entremkr": "Entremkr",
     "formType": "FormType",
     "formtype": "formtype",
     "froempment": 8,
     "frosic2007": "frosic2007",
     "frosic92": "frosic92",
     "frotover": 9,
     "inclexcl": "inclexcl",
     "legalstatus": "Legal Status",
     "name": "Runame-1 Runame-2 Runame-3",
     "region": "UK",
     "runame1": "Runame-1",
     "runame2": "Runame-2",
     "runame3": "Runame-3",
     "ruref": "831078087",
     "rusic2007": "rusic2007",
     "rusic92": "rusic92",
     "seltype": "seltype",
     "source": "test_get_business_by_search_partial_ru",
     "trading_as": "Tradstyle-1 Tradstyle-2 Tradstyle-3",
     "tradstyle1": "Tradstyle-1",
     "tradstyle2": "Tradstyle-2",
     "tradstyle3": "Tradstyle-3"
    },
  "id": "42e08c51-1d78-4524-bf39-c6523d4c0939",
  "name": "Runame-1 Runame-2 Runame-3",
  "sampleSummaryId": "831078087",
  "sampleUnitRef": "831078087",
  "sampleUnitType": "B",
  "trading_as": "Tradstyle-1 Tradstyle-2 Tradstyle-3"
}
```
<hr>

* `GET /businesses?id=d826818e-179e-467b-9936-6a8603dc8b46&id=623435fa-708e-49c0-8f90-507ac862a540`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
    
&mdash; When multiple businesses are requested this returns a concrete representation of the business parties. This representation will include any respondents associated with the business and any survey enrolments they have.

#### Example JSON Response

```json
[{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
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

<hr>

* `GET /businesses/ref/49900000001`                        

    * Must be provided a **valid** business reference in the url string.
    * An invalid reference will return a `404`.
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
    * **May** be provided with the `?verbose=true` suffix (or passed through the body) for some additional information (see below).

#####Example JSON Response

```json
{
    "associations": [
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "931e8c5a-8ed8-4ce8-a86e-e1d7693a7d65"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "f81a1c00-9445-47b8-8b21-62322e9ad331"
        ],
         ...ETC
```
#####Additional JSON with Verbose
```json
    "birthdate": "01/09/1993",
    "cellNo": 0,
    "checkletter": "F",
    "currency": "S",
    "entname1": "ENTNAME1_COMPANY1",
    "entname2": "ENTNAME2_COMPANY1",
    "entname3": "",
    "entref": "9900000576",
    "entrepmkr": "E",
    "formtype": "0001",
    "froempment": 8478,
    "frosic2007": "45320",
    "frosic92": "50300",
    "frotover": 7,
    "id": "1f5a785e-706d-433d-8a56-9d2090fb480f",
    "inclexcl": "D",
    "legalstatus": "1",
    "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
    "region": "FE",
    "runame1": "RUNAME1_COMPANY1",
    "runame2": "RUNNAME2_COMPANY1",
    "runame3": "",
    "rusic2007": "45320",
    "rusic92": "50300",
    "sampleSummaryId": "f67aedfb-e136-4aab-ba13-bbb9b6042564",
    "sampleUnitId": "d3b56391-fe47-4988-a40f-6afd06fb89b9",
    "sampleUnitRef": "49900000001",
    "sampleUnitType": "B",
    "seltype": "C",
    "trading_as": "TOTAL UK ACTIVITY",
    "tradstyle1": "TOTAL UK ACTIVITY",
    "tradstyle2": "",
    "tradstyle3": ""
```
    
<hr>
    
* `GET /businesses/id/1f5a785e-706d-433d-8a56-9d2090fb480f`

    * Must be provided a **valid** business id
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
    * **May** be provided with the `?verbose=true` suffix (or passed through the body) for some additional information (see below).

#####Example JSON Response

```json
{
    "associations": [
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "931e8c5a-8ed8-4ce8-a86e-e1d7693a7d65"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "f81a1c00-9445-47b8-8b21-62322e9ad331"
        },
        ...ETC
```
#####Additional JSON with Verbose
```json
"birthdate": "01/09/1993",
    "cellNo": 0,
    "checkletter": "F",
    "currency": "S",
    "entname1": "ENTNAME1_COMPANY1",
    "entname2": "ENTNAME2_COMPANY1",
    "entname3": "",
    "entref": "9900000576",
    "entrepmkr": "E",
    "formtype": "0001",
    "froempment": 8478,
    "frosic2007": "45320",
    "frosic92": "50300",
    "frotover": 7,
    "id": "1f5a785e-706d-433d-8a56-9d2090fb480f",
    "inclexcl": "D",
    "legalstatus": "1",
    "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
    "region": "FE",
    "runame1": "RUNAME1_COMPANY1",
    "runame2": "RUNNAME2_COMPANY1",
    "runame3": "",
    "rusic2007": "45320",
    "rusic92": "50300",
    "sampleSummaryId": "f67aedfb-e136-4aab-ba13-bbb9b6042564",
    "sampleUnitId": "d3b56391-fe47-4988-a40f-6afd06fb89b9",
    "sampleUnitRef": "49900000001",
    "sampleUnitType": "B",
    "seltype": "C",
    "trading_as": "TOTAL UK ACTIVITY",
    "tradstyle1": "TOTAL UK ACTIVITY",
    "tradstyle2": "",
    "tradstyle3": ""
 ```
 
<hr>

* `PUT /businesses/sample/link/<sampleSummaryId>`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
#### Example JSON DATA for the put
```json
{
   "collectionExerciseId": "aCollectionExerciseId"
}
```
&mdash; This endpoint will update all businesses' attributes associated collection exercise id for given sample.

#### Example JSON Response
```json
{
    "collectionExerciseId": "aCollectionExerciseId",
    "sampleSummaryId": "aSampleSummaryId"
}
```
<hr>

* `GET /businesses/search?query=bricks`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).

&mdash; This endpoint will search the database for business names that contain the `query` being passed.
##### Example JSON Response
```json
{
    "name": "RED BRICKS LTD",
    "ruref": "49900000008",
    "trading_as": ""
},
```
<hr>

####Parties Endpoints
* `POST /parties`

&mdash; Posts a new party (with sampleUnitType 'B')
##### Example JSON Schema
```json
{
    "type": "object",
    "properties": {
        "sampleUnitRef": { "type": "string" },
        "sampleUnitType": { "enum": ["B", "BI"]},
        "sampleSummaryId": { "type": "string" },
        "attributes": {
            "type": "object",
            "properties": {
                "ruref": {"type": "string"},
                "birthdate": {"type": "string"},
                "checkletter": {"type": "string"},
                "currency": {"type": "string"},
                "entname1": {"type": "string"},
                "entname2": {"type": "string"},
                "entname3": {"type": "string"},
                "entref": {"type": "string"},
                "entremkr": {"type": "string"},
                "formType": {"type": "string"},
                "formtype": {"type": "string"},
                "froempment": {"type": "integer"},
                "frosic2007": {"type": "string"},
                "frosic92": {"type": "string"},
                "frotover": {"type": "integer"},
                "inclexcl": {"type": "string"},
                "legalstatus": {"type": "string"},
                "region": {"type": "string"},
                "runame1": {"type": "string"},
                "runame2": {"type": "string"},
                "runame3": {"type": "string"},
                "rusic2007": {"type": "string"},
                "rusic92": {"type": "string"},
                "seltype": {"type": "string"},
                "tradstyle1": {"type": "string"},
                "cell_no": {"type": "integer"}
            },
            "required": ["runame1", "runame2", "runame3"]
        }
    },
    "required": ["sampleUnitRef", "sampleUnitType", "sampleSummaryId"]
}
```
<hr>

* `GET /parties/type/B/ref/499000011335`
* `GET /parties/type/B/id/d826818e-179e-467b-9936-6a8603dc8b46`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).

&mdash; When generic party type 'B' (business) is requested this returns a generic party representation of the business resource. This representation will include any respondents associated with the business and any survey enrolments they have.

##### Example JSON Response
```json
{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
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
<hr>

#####Respondents Endpoints
* `PUT /respondents/email`
* `PUT /respondents/change_email`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
    * Both URLs are linked to the same endpoint.
##### Example JSON DATA for the put
```json
{
   "email_address": "old@email.com",
   "new_email_address": "new@email.com"
}
```
&mdash; This endpoint will update a respondent's email in the ras-party database and the oauth2 server. This email will need verified again so it will also set the user as unverified in the oauth server and will send a new verification email to the respondent.

##### Example JSON Response
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
<hr>

* `POST /respondents/add-survey`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).

##### Example JSON data for post
```json
{
    "party_id": "438df969-7c9c-4cd4-a89b-ac88cf0bfdf3",
    "enrolment_code": "fb747cq725lj"
}
```
&mdash; This endpoint will enrol a respondent in a survey and associate with business if not already associated.

<hr>

* `PUT /respondents/edit-account-status/<respondent_party_id>`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).

##### Example JSON data for put
```json
{
    "status_change": "SUSPENDED"
}
```
&mdash; This endpoint will change a respondent's account status based on status_change variable.

<hr>

####Respondent Endpoints
* `GET /tokens/verify/<token>`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
    
&mdash; Endpoint to verify a users email address using a token sent to them.
##### Example JSON Response
###### Invalid Token
```json
{
    "description": "Unknown email verification token"
}
```
###### Expired Token
```json
{
    "description": "Expired email verification token"
}
```
###### Respondent not found
```json
{
    "description": "Respondent does not exist"
}
```
###### Successful
```json
{
    "response": "Ok"
}
```
<hr>

* `GET /respondents/change_password/<token>`
    * Must be prefaced with `/party-api/v1/` in url string (or current version).
    
&mdash; 
##### Example JSON Response
###### Invalid Token
```json
{
    "description": "Unknown email verification token"
}
```
###### Expired Token
```json
{
    "description": "Expired email verification token"
}
```
###### Respondent not found
```json
{
    "description": "Respondent does not exist"
}
```
###### Successful
```json
{
    "response": "Ok"
}
```
<hr>

* `POST /respondents/request_password_change`

<hr>

* `POST /respondents`

<hr>

* `PUT /emailverifcation/<token>`

<hr>

* `POST /resend-verification-email/<party_uuid>`

<hr>

* `POST /resend-verification-email/<party_uuid>`

<hr>

* `POST /resend-verification-email-expired-token/<token>`

<hr>

* `POST /resend-password-email-expired-token/<token>`

<hr>

* `POST /respondents/add_survey`

<hr>

* `PUT /respondents/change_enrolment_status`

<hr>

* `PUT /respondents/edit-account-status/<party_id>`
##### Example JSON data for put
```json
{
    "status_change": "SUSPENDED"
}
```
&mdash; This endpoint will change a respondent's account status based on status_change variable.

<hr>

* `GET /respondents`

<hr>

* `GET /respondents/id/<id>`

<hr>

* `GET /respondents/email`

<hr>

* `PUT /respondents/id/<respondent_id>`
    * Uses the party_uuid ID from the respondent table.
    * Must be prefaced with `/party-api/v1/` in url string (or current version). Must be prefaced with `/party-api/v1/` in url string (or current version).

####Example JSON Response
```json
{
    "associations": [
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "02b9c366-7397-42f7-942a-76dc5876d86d"
                },
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "2559088f-e5e3-4a7b-8c09-32197612b1ab",
            "sampleUnitRef": "49900000008"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "49d28188-f295-4d87-b8a3-c8c2bcceaaa9",
            "sampleUnitRef": "49900000007"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "13f799e7-4ac6-4415-8358-6721d7bb3e60",
            "sampleUnitRef": "49900000006"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "cb8accda-6118-4d3b-85a3-149e28960c54"
                }
            ],
            "partyId": "fa6eb819-6de8-405e-ab94-9279a01d2ddd",
            "sampleUnitRef": "49900000001"
        }
    ],
    "emailAddress": "example@example.com",
    "firstName": "first_name",
    "id": "9d3012a1-4a03-4de8-af4e-242504401b67",
    "lastName": "last_name",
    "sampleUnitType": "BI",
    "status": "ACTIVE",
    "telephone": "0987654321"
}
```

<hr>

####Info Endpoints

* `GET /info`