{{ config(materialized='table', schema='raw_main_staging') }}

with src as (
  select * from {{ source('raw', 'gtfs_calendar_attributes') }}
),

clean as (
  select
    cast(service_id as varchar) as service_id,

    nullif(trim(cast(service_description as varchar)), '') as service_description,
    nullif(trim(cast(service_schedule_name as varchar)), '') as service_schedule_name,

    -- a normalized string that is very useful for bot matching / search
    lower(
      regexp_replace(
        coalesce(service_schedule_name, '') || ' ' || coalesce(service_description, ''),
        '[^a-zA-Z0-9 ]', ' ', 'g'
      )
    ) as service_label_search
  from src
),

derived as (
  select
    *,
    case
      when service_label_search like '%weekday%' then 'Weekday'
      when service_label_search like '%weekend%' then 'Weekend'
      when service_label_search like '%saturday%' and service_label_search not like '%sunday%' then 'Saturday'
      when service_label_search like '%sunday%' and service_label_search not like '%saturday%' then 'Sunday'
      when service_label_search like '%friday%' and service_label_search not like '%monday%' then 'Friday'
      else 'Other'
    end as service_day_type
  from clean
)

select * from derived;