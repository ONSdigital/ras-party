* Assume generally that REST principles are not applied throughout, this requires addressing to deliver a truly RESTful API
* PUT /respondents/email and PUT /respondents/change_email are the same endpoint
* POST /respondents uses camel case instead of snake case for the requestBody
* POST /respondents returns 200 for creating a respondent instead of 201
* to_respondent_dict/to_respondent_with_associations_dict/to_party_dict all return in camel case instead of snake case
* POST /respondents returns 500 when it can't find the business to associate with instead of 404
* PUT /emailverification/whatever should probably be /email-verification/whatever
* POST /respondents/add_survey should probably be /respondents/add-survey
* No consistency on the do something endpoints, e.g. PUT /emailverification/token but POST /resend-verification-email/party-uuid
* PUT /respondents/change_enrolment_status change case
* No consistency on party_id vs respondent_id
* PATCH /respondents/disable-user-enrolments returns 422 instead of 409 for multiple respondents found
* POST /pending-survey-respondent has a mix of camel case and snake case parameters in requestBody
* The pending survey stuff in general is a mess
* GET /respondent/email has the email in a requestBody instead of the URL or query parameters for some unknown reason