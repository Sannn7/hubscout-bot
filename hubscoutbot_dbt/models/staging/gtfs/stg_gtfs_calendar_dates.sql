{{ config(materialized='table', schema='raw_main_staging') }}

with src as (
  select * from {{ source('raw', 'gtfs_calendar_dates') }}
),

typed as (
  select
    cast(service_id as varchar) as service_id,
    strptime(cast(date as varchar), '%Y%m%d')::date as date,
    cast(exception_type as int) as exception_type,
    nullif(trim(cast noting? as varchar), '') as holiday_name
  from src
),

derived as (
  select
    *,
    (holiday_name is not null) as is_holiday,
    coalesce(holiday_name, 'No holiday') as holiday_name_filled,
    case
      when exception_type = 1 then 'Added service'
      when exception_type = 2 then 'Removed service'
      else 'Unknown'
    end as exception_type_label
  from typed
)

select * from derived;