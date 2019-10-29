alter table partysvc.business_attributes
add column IF NOT EXISTS name text,
add column IF NOT EXISTS trading_as text ;


create index  IF NOT EXISTS attributes_name_idx on partysvc.business_attributes(name);
create index  IF NOT EXISTS attributes_trading_as_idx on partysvc.business_attributes(trading_as);

