{{ config(materialized='table', schema='raw_main_staging') }}

with src as (
  select * from {{ source('raw', 'gtfs_facilities') }}
),

clean as (
  select
    cast(facility_id as varchar) as facility_id,
    cast(facility_code as varchar) as facility_code,
    cast(facility_class as int) as facility_class,

    nullif(trim(cast(facility_type as varchar)), '') as facility_type,
    nullif(trim(cast(stop_id as varchar)), '') as stop_id,

    nullif(trim(cast(facility_short_name as varchar)), '') as facility_short_name,
    nullif(trim(cast(facility_long_name as varchar)), '') as facility_long_name,
    nullif(trim(cast(facility_desc as varchar)), '') as facility_desc,

    try_cast(facility_lat as double) as facility_lat,
    try_cast(facility_lon as double) as facility_lon,

    try_cast(wheelchair_facility as int) as wheelchair_facility
  from src
),

derived as (
  select
    *,
    lower(regexp_replace(coalesce(facility_type, ''), '[^a-zA-Z0-9 ]', ' ', 'g')) as facility_type_search,
    lower(regexp_replace(coalesce(facility_long_name, ''), '[^a-zA-Z0-9 ]', ' ', 'g')) as facility_name_search,

    case
      when wheelchair_facility is null then 'Unknown'
      else 'Code ' || cast(wheelchair_facility as varchar)
    end as wheelchair_facility_label
  from clean
)

select * from derived;