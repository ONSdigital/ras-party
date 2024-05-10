# Party Service API

## Business Endpoints

### Create or Update a Business

* `POST /party-api/v1/businesses`
  * In the case of a new business, stores the new business data.
  * In the case of a known business then it adds the versioned attributes.
  * Input data is validated against `party_schema.json` which mandates that `sampleUnitRef`, `sampleUnitType` and `sampleSummaryId` are mandatory.
  * If attributes are provided then `runname1`,`runname2` and `runname3` are mandatory

#### Example JSON Response

```json
{
  "associations": [],
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

### Get Business details by ID (Query String)

* `GET /party-api/v1/businesses?id=<id>`
  * Returns details about a list of business by id. Returns a concrete representation of the business parties. This representation will include any respondents associated with the business and any survey enrolments they have.

#### Example JSON Response

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

### Get Business Details by Reference Number

* `GET /businesses/ref/<ref>` OR `GET /party-api/v1/parties/type/B/ref/<ref>`
  * Gets business information from reference number.
  * Must be provided a **known** business reference in the url string.
  * An **unknown** reference will return a `404`.

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
        }
    ],
    "id": "<id>",
    "name": "RUNAME1_COMPANY1 RUNNAME2_COMPANY1",
    "sampleSummaryId": "<sampleSummaryId>",
    "sampleUnitId": "<sampleUnitId>",
    "sampleUnitRef": "<sampleUnitRef>",
    "sampleUnitType": "B",
    "trading_as": "TOTAL UK ACTIVITY",
}
```

---

### Get Business Details by ID (URL)

* `GET /party-api/v1/businesses/id/<id>`
  * Provides business details from business ID.
  * Must be provided a **known** business id.
  * **Optional attribute:** `?verbose=true` also returns `attributes`, see below.

#### Example JSON Response

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
        }
                  ]
}
```

#### Example JSON response with `verbose=true`

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

### Get Business attributes by ID (URL)

* `GET /party-api/v1/businesses/id/<id>/attributes`
  * Provides business attribute details for a reporting unit by id.
  * If the business_id isn't found, it WILL NOT return an error.
  * **Optional attribute:** `?collection_exercise_id=<uuid>`.  This can be repeated many times to get a list of attributes
  for only specific collection exercises
  * It will return a dictionary of data with the collection exercise as the key.
  * Any collection exercises not found will not be included in the result but WILL NOT return an error

Returns:
  * 200 - On success
  * 400 - If the business id or any of the collection_exercise_id's aren't a valid uuid's

#### Example JSON Response

```json
{
  "14fb3e68-4dca-46db-bf49-04b84e07e77c": {
    "id": "1",
    "business_id": "b3ba864b-7cbc-4f44-84fe-88dc018a1a4c",
    "sample_summary_id": "3eff4678-a8d1-41fd-b986-4e497de9bbda",
    "collection_exercise": "14fb3e68-4dca-46db-bf49-04b84e07e77c",
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
      "currency": "H"
    },
    "created_on": "2020-06-16T10:19:13.152Z",
    "name": "Bolts and Ratchets Ltd",
    "trading_as": "Bolts and Ratchets Ltd"
  }
}
 ```

---

### Delete business attributes by sample_summary_id

* `DELETE /party-api/v1/businesses/attributes/sample-summary/<sample_summary_id>`
  * Deletes all the attribute records that have matching sample_summary_id
  * Will return a 204 even if there are no records with the provided id.

Returns:
  * 204 - On success, regardless of whether it deleted any records or not
  * 400 - If the id provided isn't a valid uuid

---

### Store Association Between Business, Collection & Sample

* `PUT /party-api/v1/businesses/sample/link/<sampleSummaryId>`
  * Stores an association between a business, collection exercise and a sample
  * the sample data is passed in the body

#### Example JSON payload

```json
{
   "collectionExerciseId": "aCollectionExerciseId"
}
```

#### Example JSON Response

```json
{
    "collectionExerciseId": "aCollectionExerciseId",
    "sampleSummaryId": "aSampleSummaryId"
}
```

---

### Get Business details (query)

* `GET /party-api/v1/businesses/search?query=bricks`
  * Returns `name`, `ruref` and `trading as` for those businesses which match the `query_params`.
  * `query_params` is a list of search words.
  * Matches are found if the business `name`, `trading` as or `business_ref` contains the param.
  * All Params in `query_params` must be matched.

#### Example JSON Query

```json
{
  "query": "bricks"
}
```

#### Example JSON Response

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

#### Example JSON Schema

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
                "name": {"type": "string"},
                "region": {"type": "string"},
                "runame1": {"type": "string"},
                "runame2": {"type": "string"},
                "runame3": {"type": "string"},
                "rusic2007": {"type": "string"},
                "rusic92": {"type": "string"},
                "seltype": {"type": "string"},
                "trading_as": {"type": "string"},
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
        "name": "ENTNAME1 ENTNAME2 ENTNAME3",
        "runame1": "Bolts",
        "runame2": "and",
        "runame3": "Ratchets Ltd",
        "trading_as": "trading_as",
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

#### Example JSON payload

```json
{
   "email_address": "old@email.com",
   "new_email_address": "new@email.com"
}
```

#### Example JSON Response

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

### Add respondent to survey

* `POST /party-api/v1/respondents/add-survey`
  * This endpoint will enrol a respondent in a survey and associate with business if not already associated.

#### Example JSON payload

```json
{
    "party_id": "<party_id>",
    "enrolment_code": "<enrolment_code>"
}
```

---

## Respondent Endpoints

### Verify Token

* `GET /party-api/v1/tokens/verify/<token>`
  * Verifies a users token when provided with a **known** token.
  * Token will have been sent to them via email.

#### Example JSON Response

##### Invalid Token

```json
{
    "description": "Unknown email verification token",
  
}
```

##### Expired Token

```json
{
    "description": "Expired email verification token"
}
```

##### Respondent not found

```json
{
    "description": "Respondent does not exist"
}
```

##### Successful

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

#### Example JSON Response

##### Invalid Token

```json
{
    "description": "Unknown email verification token"
}
```

##### Expired Token

```json
{
    "description": "Expired email verification token"
}
```

##### Respondent not found

```json
{
    "description": "Respondent does not exist"
}
```

##### Successful

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

### Respondents enrolled in a survey for a business

* `GET /respondents/survey_id/<survey_id>/business_id/<business_id>`
  * returns a list of Respondents enrolled in a survey for a specified business id.

### Example JSON Response

```json
[
   {
      "id":"0bdcda6c-5d5c-43bf-9ebd-7085b37f9035",
      "sampleUnitType":"BI",
      "emailAddress":"a@z.com",
      "firstName":"A",
      "lastName":"Z",
      "telephone":"123",
      "status":"CREATED",
      "associations":[
         {
            "partyId":"3b136c4b-7a14-4904-9e01-13364dd7b972",
            "sampleUnitRef":"49000000000",
            "businessRespondentStatus":"CREATED",
            "enrolments":[
               {
                  "surveyId":"cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
                  "enrolmentStatus":"ENABLED"
               }
            ]
         }
      ],
      "password_verification_token":"ImFAei5jb20i.Zj3biA.PAgq3GiYIdfeUywntZS7EDeKIzY",
      "password_reset_counter":1
   }
]
```

---

### Create New Party

* `POST /party-api/v1/respondents`
  * Posts a respondent to the database and generates their `sampleUnitRef`, `partyID` and `enrolments`.
  * If passed an `id` parameter it will use this instead of generating a new UUID.
  * Sets `businessRespondentStatus` to 'CREATED'.
  * Returns a 200 on success, a 400 if data is missing or iac is invalid and 409 if the user email already exists.

#### Example JSON Payload

```json
[
  {
    "emailAddress" : "example@example.com",
    "firstName" : "Bob",
    "lastName" : "Dabilder",
    "password" : "password",
    "telephone" : "01234567890",
    "enrolmentCode" : "<enrolmentCode>",
  }
]

```

---

### Verify Email Address with Token

* `PUT /emailverification/<token>`
  * Verifies the users email address against a provided token.
  * Example token: `'ImFAei5jb20i.W-7Ovg.hFZ7nhkzq8e7i76EXSwgvJQXAjs'`

#### Example JSON Response

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

#### Example JSON Response

```json
{
  "message": "A new verification email has been sent"
}
```

---

### Re-send Verification Email (Token Expired)

* `POST /resend-verification-email-expired-token/<token>`
  * Allows an internal user to send another verification email to respondent.

#### Example JSON Response

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

#### Example JSON Response

```json
{
  "response":"ok"
}
```

---

### Add Survey to Respondent

* `POST /party-api/v1/respondents/add_survey`
  * Adds a survey to an existing respondent.

### Example JSON payload

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

#### Example JSON payload

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

#### Example JSON data

```json
{
    "status_change": "SUSPENDED"
}
```

---

### Get Respondent Info

* `GET /party-api/v1/respondents?id=<id>&firstname=<firstname>&lastname=<lastname>&emailAddress=<emailAddress>`
  * Returns respondents info based on passed in params.
  * id is the party ids of a list of respondents.
    * Uses party_uuid from respondent table.
    * The endpoint uses parameter name `id` instead of `partyId`.
    * id is mutually exclusive to username an email . if id is present and either username.
    or email then a 400 will be returned
    * Each id must be a uuid.
  * firstName . A first name or part first name of a respondent. If present will restrict the returned results.
to those respondents whose first name starts with the `firstName` value, case insensitive.
    * If present and zero length then 400 returned
  * lastName . A last name or part last name of a respondent. If present will restrict the returned results.
to those respondents whose last name starts with the `lastName` value, case insensitive.  
    * If present and zero length then 400 returned
  * emailAddress . An email address or partial email address . If present it will restrict respondents
to those that contain the `emailAddress` value, case insensitive.
    *If present and zero length then 400 returned
  * page . The page of data to return ( 1 based) . If not supplied defaults to 1
  * limit . The maximum number of rows to return . If not supplied, defaults to 10

Note: The returned data for get by id end points does not return the total record count. The get by name and emails does.
This is to ease pagination in the ui.

#### Example JSON Response Get by id

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

#### Example JSON Response Get by firstName, lastName and emailAddress

Note use of data and total elements . Where total is the total number of records satisfying the filter criteria.
To get the total number of pages divide total by limit and round up . E.g there are 27 records matching a search crietria , but we have page set to 3 and limit set to 5 . Then there would be 5 records in data but
total would be 27

```json
{"data":[
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
    }],
    total:389
}

```

---

### Get Respondent Info by ID

* `GET /party-api/v1/respondents/id/<id>`
  * Returns respondent by the the ID provided.
  * Uses the party_uuid from the respondent table.

#### Example JSON Response

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

### Delete Respondent by Email

* `DELETE /party-api/v1/respondents/email`
  * Deletes a respondent by their email address.
  * Returns a 204 on success, a 400 if the id isn't a valid uuid and 404 if the user cannot be found.

---

### Disable all user enrolments by email

* `PATCH /party-api/v1/respondents/disable-user-enrolments`
  * Disables all active enrolments for a respondent based on their email address.
  * Returns a 204 on success, a 400 if the id isn't a valid uuid and 404 if the user cannot be found.

---

### Get Respondent Info by Email

* `GET /party-api/v1/respondents/email`
  * Returns respondent information with an `emailAddress` key.
  * Must be sent `'email'` parameter in the body of the request.
  * If email is not found returns a `404`

#### Example JSON Response

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

### Get Respondent Claim

* 'GET /party-api/v1/respondents/claim'
  * respondent_id required param
  * business_id required param
  * survey_id required param

Validates if the specific respondent has a claim on a specific business and survey.
Uses returned data to determine validity rather than hijack http status code.
(Not a restful endpoint: status code 200/403 is alternative)
Returns:
    * 200 if the state of the users claim is known.
        returns "Valid" or "Invalid" in body
    * 400 if incorrect parameters

### Update Respondent Info

* `PUT /party-api/v1/respondents/id/<respondent_id>`
  * Updates a respondent's details (first name, last name, telephone and email) based on `party_uuid` from the respondents table.

#### Example JSON payload

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
### Get Respondent Token
* `GET /party-api/v1/respondents/<respondent_id>/verification-token`
  * Retrieves a respondent's valid verification token based on `party_uuid`

### Success
```json
{
  "token": "<token>"
}
```
---
  
### Add Respondent Token
* `POST /party-api/v1/respondents/<respondent_id>/verification-token`
  * Updates a respondent's valid verification token based on `party_uuid`
  * Increases a respondent's password reset token base on `party_uuid`

#### Example JSON payload

```json
{
  "token": "<token>"
}
```

---
### Delete Respondent Token
* `DELETE /party-api/v1/respondents/<respondent_id>/verification-token/<token>`
  * Updates a respondent's valid verification token based on `party_uuid` deduced from the `email` passed.

---

---
### Get Password Reset Counter
* `GET /party-api/v1/respondents/<respondent_id>/password-reset-counter`
  * Retrieves a respondent's password reset counter based on the `party_uuid`

### Success
```json
{
  "counter": "<counter>"
}
```
---

---
### Delete Password Reset Counter
* `DELETE /party-api/v1/respondents/<respondent_id>/password-reset-counter`
  * Resets a respondent's password reset counter based on the `party_uuid`
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
    "version": "1.9.0"
}
```
