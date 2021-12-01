CREATE EXTENSION pg_trgm;
CREATE INDEX attributes_name_gin_trgm_idx ON partysvc.business_attributes USING gin (name gin_trgm_ops);
CREATE INDEX attributes_trading_as_gin_trgm_idx ON partysvc.business_attributes USING gin (trading_as gin_trgm_ops);
CREATE INDEX business_ru_gin_trgm_idx ON partysvc.business USING gin (business_ref gin_trgm_ops);

