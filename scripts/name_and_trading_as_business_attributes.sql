alter table partysvc.business_attributes
add column name text,
add column trading_as text;

create index attributes_name_idx on partysvc.business_attributes(name);
create index attributes_trading_as_idx on partysvc.business_attributes(trading_as);

