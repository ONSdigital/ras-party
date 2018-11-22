# Party Service API

### *Acceptance tests can be run to populate a local version with test data.*

---

## Business Endpoints:

### Create or Update a Business.
* `POST /party-api/v1/businesses`
    * In the case of a new business, stores the new business data. 
    * In the case of a known business then it adds the versioned attributes.
    * Input data is validated against `party_schema.json` which mandates that `sampleUnitRef`, `sampleUnitType` and `sampleSummaryId` are mandatory.
    * If attributes are provided then `runname1`,`runname2` and `runname3` are mandatory 
### Example JSON Response
```json
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
  "id": "<id>",
  "name": "Runame-1 Runame-2 Runame-3",
  "sampleSummaryId": "<sampleSummaryId>",
  "sampleUnitRef": "<sampleUnitRef>",
  "sampleUnitType": "B",
  "trading_as": "Tradstyle-1 Tradstyle-2 Tradstyle-3"
}
```
---
### Get Business details by ID (Query String).
* `GET /party-api/v1/businesses?id=<id>`
    * Returns details about a list of business by id. Returns a concrete representation of the business parties. This representation will include any respondents associated with the business and any survey enrolments they have.
### Example JSON Response

```json
[{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "surveyId": "<surveyId>"
            }
        ],
        "partyId": "<partyId>",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "name": "Bolts and Ratchets Ltd",
    "id": "<id>",
    "sampleUnitRef": "<sampleUnitRef>",
    "sampleUnitType": "B"
},
{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "surveyId": "<surveyId>"
            }
        ],
        "partyId": "<partyId>",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "name": "Example Ltd",
    "id": "<id>",
    "sampleUnitRef": "<sampleUnitRef>",
    "sampleUnitType": "B"
}]
```

---
### Get Business Details by Reference Number.
* `GET /businesses/ref/<ref>`                        
    * Gets business information from reference number.
    * Must be provided a **known** business reference in the url string.
    * An **unknown** reference will return a `404`.
    * **Optional attribute:** `?verbose=true` also returns `attributes`, see below.

### Example JSON Response

```json
{
    "associations": [
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>"
                    ],
```
### Additional JSON with Verbose
```json
 {
 
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
    "id": "<id>",
    "inclexcl": "D",
    "legalstatus": "1",
    "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
    "region": "FE",
    "runame1": "RUNAME1_COMPANY1",
    "runame2": "RUNNAME2_COMPANY1",
    "runame3": "",
    "rusic2007": "45320",
    "rusic92": "50300",
    "sampleSummaryId": "<sampleSummaryId>",
    "sampleUnitId": "<sampleUnitId>",
    "sampleUnitRef": "<sampleUnitRef>",
    "sampleUnitType": "B",
    "seltype": "C",
    "trading_as": "TOTAL UK ACTIVITY",
    "tradstyle1": "TOTAL UK ACTIVITY",
    "tradstyle2": "",
    "tradstyle3": ""
}
```
    
---
### Get Business Details by ID (URL)    
* `GET /party-api/v1/businesses/id/<id>`
    * Provides business details from business ID.
    * Must be provided a **known** business id.
    * **Optional attribute:** `?verbose=true` also returns `attributes`, see below.
    
### Example JSON Response

```json
{
    "associations": [
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>"
        },
        ...ETC
```
### Additional JSON with Verbose
```json
{

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
    "id": "<id>",
    "inclexcl": "D",
    "legalstatus": "1",
    "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
    "region": "FE",
    "runame1": "RUNAME1_COMPANY1",
    "runame2": "RUNNAME2_COMPANY1",
    "runame3": "",
    "rusic2007": "45320",
    "rusic92": "50300",
    "sampleSummaryId": "<sampleSummaryId>",
    "sampleUnitId": "<sampleUnitId>",
    "sampleUnitRef": "<sampleUnitRef>",
    "sampleUnitType": "B",
    "seltype": "C",
    "trading_as": "TOTAL UK ACTIVITY",
    "tradstyle1": "TOTAL UK ACTIVITY",
    "tradstyle2": "",
    "tradstyle3": ""
    }
 ```
 
---
### Store Association Between Business, Collection & Sample.
* `PUT /party-api/v1/businesses/sample/link/<sampleSummaryId>`
    * Stores an association between a business, collection exercise and a sample
    * the sample data is passed in the body

### Example JSON DATA for the put
```json
{
   "collectionExerciseId": "aCollectionExerciseId"
}
```

### Example JSON Response
```json
{
    "collectionExerciseId": "aCollectionExerciseId",
    "sampleSummaryId": "aSampleSummaryId"
}
```
---

* `GET /party-api/v1/businesses/search?query=bricks`
    * Returns `name`, `ruref` and `trading as` for those businesses which match the `query_params`.
    * `query_params` is a list of search words.
    * Matches are found if the business `name`, `trading` as or `business_ref` contains the param. 
        * All Params in `query_params` must be matched.
        
### Example JSON Query
```json
{
  "query": "bricks"
}
```

### Example JSON Response
```json
{
    "name": "RED BRICKS LTD",
    "ruref": "<ruref>",
    "trading_as": ""
}
```
---

## Parties Endpoints
### Post a New Party
* `POST /party-api/v1/parties`
    * Posts a new party (with sampleUnitType 'B')
    
### Example JSON Schema
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
---
### Get Party Details
* `GET /party-api/v1/parties/type/B/ref/<ref>`
    * When generic party type 'B' (business) is requested this returns a generic party representation of the business resource. This representation will include any respondents associated with the business and any survey enrolments they have.
* `GET /party-api/v1/parties/type/B/id/<id>`
    * Same response as above but requires a `party_uuid` rather than a ref.

### Example JSON Response
```json
{
    "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "surveyId": "<surveyId>"
            }
        ],
        "partyId": "<partyId>",
        "businessRespondentStatus": "ACTIVE"
        }
    ],
    "attributes": {
        "ruref": "<ruref>",
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
    "id": "<id>",
    "sampleUnitRef": "<sampleUnitRef>",
    "sampleUnitType": "B",
    "name": "Bolts and Ratchets Ltd"
}
```
---

## Respondents Endpoints
### Change a Respondents Email
* `PUT /party-api/v1/respondents/email`
* `PUT /party-api/v1/respondents/change_email`
    * Changes a respondents old email address to a new provided one.
        * Both the current email '`email_address`' and the '`new_email_address`' are to be provided in the body.
    * Both URLs are linked to the same endpoint.
    * This endpoint will update a respondent's email in the ras-party database and will send a new verification email to the respondent.
### Example JSON DATA for the put
```json
{
   "email_address": "old@email.com",
   "new_email_address": "new@email.com"
}
```


### Example JSON Response
```json
{
   "emailAddress": "testtest@test.test",
   "firstName": "Test",
   "id": "<id>",
   "lastName": "tseT",
   "sampleUnitType": "BI",
   "status": "ACTIVE",
   "telephone": "07846608000"
}
```
---

* `POST /party-api/v1/respondents/add-survey`
    * This endpoint will enrol a respondent in a survey and associate with business if not already associated.

### Example JSON data for post
```json
{
    "party_id": "<party_id>",
    "enrolment_code": "<enrolment_code>"
}
``` 

---

## Respondent Endpoints
### Verify  Token
* `GET /party-api/v1/tokens/verify/<token>`
    * Verifies a users token when provided with a **known** token.
        * Token will have been sent to them via email.   
    
### Example JSON Response
#### Invalid Token
```json
{
    "description": "Unknown email verification token"
}
```
#### Expired Token
```json
{
    "description": "Expired email verification token"
}
```
#### Respondent not found
```json
{
    "description": "Respondent does not exist"
}
```
#### Successful
```json
{
    "response": "Ok"
}
```
---
### Respondent Change Password
* `GET /party-api/v1/respondents/change_password/<token>`
    * Lets a user change their login password with a **known** token.
        * Token will have been sent to them via email.
    
### Example JSON Response
#### Invalid Token
```json
{
    "description": "Unknown email verification token"
}
```
#### Expired Token
```json
{
    "description": "Expired email verification token"
}
```
#### Respondent not found
```json
{
    "description": "Respondent does not exist"
}
```
#### Successful
```json
{
    "response": "Ok"
}
```
---
### Respondent Request Password Change
* `POST /party-api/v1/respondents/request_password_change`
    * Sends password reset link to the provided email address.
    * Raises an error if email not found in DB.
    * Requires `email_address` param.

### Example JSON Payload
```json
[
  {
  "email_address" : "a@z.com"
  }
]
```

### Example JSON Response
```json
{
  "response" : "ok"
}
```
---
### Create New Party
* `POST /party-api/v1/respondents`
    * Posts a respondent to the database and generates their `sampleUnitRef`, `partyID` and `enrolments`.
    * If passed an `id` parameter it will use this instead of generating a new UUID.
    * Sets `businessRespondentStatus` to 'CREATED'.

### Example JSON Payload
```json
[
  {
    "emailAddress" : "example@example.com",
    "firstName" : "Bob",
    "lastName" : "Dabilder",
    "password" : "password",
    "telephone" : "01234567890",
    "enrolmentCode" : "<enrolmentCode>",
    "sampleUnitType" : "BI"
  }
]

```
---
### Verify Email Address with Token
* `PUT /emailverification/<token>`
    * Verifies the users email address against a provided token.
    * Example token: `'ImFAei5jb20i.W-7Ovg.hFZ7nhkzq8e7i76EXSwgvJQXAjs'`
    
### Example JSON Response
```json
{
  "id": "<id>",
  "sampleUnitType": "BI",
  "pendingEmailAddress": "",
  "emailAddress": "a@z.com",
  "firstName": "Hollie",
  "lastName": "Day",
  "telephone": "01234567890",
  "status": "ACTIVE",
  "associations": [
        {
        "enrolments": [
            {
                "enrolmentStatus": "ENABLED",
                "surveyId": "<surveyId>"
            }
        ],
        "partyId": "<partyId>",
        "businessRespondentStatus": "ACTIVE"
        }
    ]
        }
```

---
### Re-send Verification Email
* `POST /resend-verification-email/<party_uuid>`
    * Sends another email containing a verification token.
    * Raises an error if email is not found in DB.
    
### Example JSON Response
```json
{
  "message": "A new verification email has been sent"
}
```

---
### Re-send Verification Email (Token Expired)
* `POST /resend-verification-email-expired-token/<token>`
    * Allows an internal user to send another verification email to respondent.

### Example JSON Response
```json
{
  "message": "A new verification email has been sent"
}
```
---
### Re-send Password Email (Token Expired)
* `POST /resend-password-email-expired-token/<token>`
    * Sends the respondent another password verification URL containing a token via email.
    * Gets the email address from the token.

### Example JSON Response
```json
{
  "response":"ok"
}
```
---
### Add Survey to Respondent
* `POST /party-api/v1/respondents/add_survey`
    * Adds a survey to an existing respondent.
### Example JSON for Post
```json
{
  "party_id": "<party_id>",
  "enrolment_code": "<enrolment_code>"
}
```

---
### Change Respondent Enrolment Status
* `PUT /party-api/v1/respondents/change_enrolment_status`
    * Allows a user to change the enrolment status of a respondent.
        * Typically 'ENABLED' or 'DISABLED' although not enforced.
        * Changed by `change_flag`
        
### Example JSON for Put
```json
{
 "respondent_id" : "<respondent_id>",
 "business_id" : "<business_id>",
 "survey_id" : "<survey_id>",
 "change_flag": "DISABLED"
  }
```
---
### Respondent Edit Account Status
* `PUT /party-api/v1/respondents/edit-account-status/<party_id>`
    * This endpoint will change a respondent's account status based on `status_change` parameter.
    * Currently used status values: `ACTIVE` `SUSPENDED`.
### Example JSON data for put
```json
{
    "status_change": "SUSPENDED"
}
```


---
### Get Respondent Info
* `GET /party-api/v1/respondents?id=<id>`
    * Returns respondent info based on a `partyId` key.
    * Uses party_uuid from respondent table.
    * The endpoint uses parameter name `id` instead of `partyId`.
   
    
### Example JSON Response
```json
[
    {
        "associations": [
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [
                    {
                        "enrolmentStatus": "ENABLED",
                        "surveyId": "<surveyId>"
                    },
                    {
                        "enrolmentStatus": "ENABLED",
                        "surveyId": "<surveyId>"
                    }
                ],
                "partyId": "<partyId>",
                "sampleUnitRef": "<sampleUnitRef>"
            },
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [
                    {
                        "enrolmentStatus": "ENABLED",
                        "surveyId": "<surveyId>"
                    }
                ],
                "partyId": "<partyId>",
                "sampleUnitRef": "<sampleUnitRef>"
            },
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [
                    {
                        "enrolmentStatus": "ENABLED",
                        "surveyId": "<surveyId>"
                    }
                ],
                "partyId": "<partyId>",
                "sampleUnitRef": "<sampleUnitRef>"
            },
            {
                "businessRespondentStatus": "ACTIVE",
                "enrolments": [
                    {
                        "enrolmentStatus": "ENABLED",
                        "surveyId": "<surveyId>"
                    }
                ],
                "partyId": "<partyId>",
                "sampleUnitRef": "<sampleUnitRef>"
            }
        ],
        "emailAddress": "example@example.com",
        "firstName": "first_name",
        "id": "<id>",
        "lastName": "last_name",
        "sampleUnitType": "BI",
        "status": "ACTIVE",
        "telephone": "0987654321"
    }
]
```

---
### Get Respondent Info by ID
* `GET /party-api/v1/respondents/id/<id>`
    * Returns respondent by the the ID provided.
    * Uses the party_uuid from the respondent table.
   

### Example JSON Response
```json
{
    "associations": [
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                },
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>",
            "sampleUnitRef": "<sampleUnitRef>"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>",
            "sampleUnitRef": "<sampleUnitRef>"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>",
            "sampleUnitRef": "<sampleUnitRef>"
        },
        {
            "businessRespondentStatus": "ACTIVE",
            "enrolments": [
                {
                    "enrolmentStatus": "ENABLED",
                    "surveyId": "<surveyId>"
                }
            ],
            "partyId": "<partyId>",
            "sampleUnitRef": "<sampleUnitRef>"
        }
    ],
    "emailAddress": "example@example.com",
    "firstName": "first_name",
    "id": "<id>",
    "lastName": "last_name",
    "sampleUnitType": "BI",
    "status": "ACTIVE",
    "telephone": "0987654321"
}
```


---
### Get Respondent Info by Email
* `GET /party-api/v1/respondents/email`
    * Returns respondent information with an `emailAddress` key.
    * Must be sent `'email'` parameter in the body of the request.
    * If email is not found returns a `404` 
### Example JSON Response
```json
 [
  {
    "emailAddress": "example@example.com",
    "firstName": "first_name",
    "id": "<id>",
    "lastName": "last_name",
    "sampleUnitType": "BI",
    "status": "ACTIVE",
    "telephone": "0987654321"
    }
 ]
```

---
### Update Respondent Info
* `PUT /party-api/v1/respondents/id/<respondent_id>`
    * Updates a respondents details (first name, last name, telephone and email) based on `party_uuid` from the respondents table.
    
### Example JSON for Put
```json
{
  "firstName": "John",
  "lastName": "Snow",
  "telephone": "0783720942",
  "email_address": "a@b.com",
  "new_email_address": "john.snow@thisemail.com"
}
```
---

## Info Endpoints
### Get Service Information
* `GET /info`
    * Returns service information.
    * Doesn't require any parameters.
    * Doesn't require `/party-api/v1/` prefix.

### Example JSON Response
```json
{
    "name": "ras-party",
    "version": "1.4.0"
}
```