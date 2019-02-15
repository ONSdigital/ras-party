CREATE INDEX respondent_email_idx ON partysvc.respondent USING btree (email_address COLLATE pg_catalog."default") TABLESPACE pg_default;

CREATE INDEX respondent_first_name_idx ON partysvc.respondent USING btree (first_name COLLATE pg_catalog."default") TABLESPACE pg_default;

CREATE INDEX respondent_last_name_idx ON partysvc.respondent USING btree (last_name COLLATE pg_catalog."default") TABLESPACE pg_default;


