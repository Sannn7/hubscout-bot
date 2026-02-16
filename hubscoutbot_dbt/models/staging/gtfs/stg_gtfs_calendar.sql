{{ config(materialized='table', schema='raw_main_staging') }}

select
  -- keep identifiers as-is
  service_id,

  -- keep the 0/1 columns as-is
  cast(monday as integer)    as monday,
  cast(tuesday as integer)   as tuesday,
  cast(wednesday as integer) as wednesday,
  cast(thursday as integer)  as thursday,
  cast(friday as integer)    as friday,
  cast(saturday as integer)  as saturday,
  cast(sunday as integer)    as sunday,

  -- parse dates (raw is YYYYMMDD)
  strptime(cast(start_date as varchar), '%Y%m%d') as start_date,
  strptime(cast(end_date as varchar), '%Y%m%d')   as end_date,

  -- NEW: number of days per week this service runs (0..7)
  (
    cast(monday as integer) +
    cast(tuesday as integer) +
    cast(wednesday as integer) +
    cast(thursday as integer) +
    cast(friday as integer) +
    cast(saturday as integer) +
    cast(sunday as integer)
  ) as service_days_per_week,

  -- OPTIONAL: inclusive duration of the date range in days
  (
    datediff('day',
      strptime(cast(start_date as varchar), '%Y%m%d'),
      strptime(cast(end_date as varchar), '%Y%m%d')
    ) + 1
  ) as service_duration_days

from {{ source('raw','gtfs_calendar') }}