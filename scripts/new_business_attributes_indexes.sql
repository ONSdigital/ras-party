
CREATE INDEX attributes_business_idx ON partysvc.business_attributes USING btree  (business_id)  TABLESPACE pg_default;
CREATE INDEX attributes_sample_summary_idx ON partysvc.business_attributes USING btree  (sample_summary_id)  TABLESPACE pg_default;
CREATE INDEX attributes_business_sample_idx ON partysvc.business_attributes USING btree (business_id, sample_summary_id COLLATE pg_catalog."default") TABLESPACE pg_default;
CREATE INDEX attributes_collection_exercise_idx ON partysvc.business_attributes USING btree  (collection_exercise)  TABLESPACE pg_default;
CREATE INDEX attributes_created_on_idx ON partysvc.business_attributes USING btree  (created_on)  TABLESPACE pg_default;


CREATE INDEX enrolment_business_idx ON partysvc.enrolment USING btree (business_id) TABLESPACE pg_default;
CREATE INDEX enrolment_respondent_idx ON partysvc.enrolment USING btree (respondent_id) TABLESPACE pg_default;
CREATE INDEX enrolment_survey_idx ON partysvc.enrolment USING btree (survey_id) TABLESPACE pg_default;
CREATE INDEX enrolment_status_idx ON partysvc.enrolment USING btree (status) TABLESPACE pg_default;

CREATE INDEX pending_enrolment_case_idx ON partysvc.pending_enrolment USING btree (case_id)  TABLESPACE pg_default;

CREATE INDEX business_respondent_idx ON partysvc.business_respondent USING btree (respondent_id) TABLESPACE pg_default;
