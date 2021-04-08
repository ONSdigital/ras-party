CREATE TABLE partysvc.pending_shares (
    email_address text NOT NULL,
    business_id uuid NOT NULL,
    survey_id text,
	time_shared TIMESTAMP,
	shared_by uuid NOT NULL,
	batch_no uuid NOT NULL,
	CONSTRAINT u_constraint UNIQUE (email_address, business_id, survey_id),
	CONSTRAINT fk_business
      FOREIGN KEY(business_id)
	  REFERENCES partysvc.business(party_uuid),
	CONSTRAINT fk_respondent
      FOREIGN KEY(shared_by)
	  REFERENCES partysvc.respondent(party_uuid));