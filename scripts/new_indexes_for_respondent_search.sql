CREATE INDEX IF NOT EXISTS respondent_email_idx ON partysvc.respondent USING btree (email_address COLLATE pg_catalog."default") TABLESPACE pg_default;

CREATE INDEX  IF NOT EXISTS respondent_first_name_idx ON partysvc.respondent USING btree (first_name COLLATE pg_catalog."default") TABLESPACE pg_default;

CREATE INDEX  IF NOT EXISTS respondent_last_name_idx ON partysvc.respondent USING btree (last_name COLLATE pg_catalog."default") TABLESPACE pg_default;


