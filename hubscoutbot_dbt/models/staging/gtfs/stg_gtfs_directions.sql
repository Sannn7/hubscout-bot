{{ config(materialized='table', schema='raw_main_staging') }}

with src as (
  select * from {{ source('raw', 'gtfs_directions') }}
),

clean as (
  select
    cast(route_id as varchar) as route_id,
    cast(direction_id as int) as direction_id,
    nullif(trim(cast(direction as varchar)), '') as direction,
    nullif(trim(cast(direction_destination as varchar)), '') as direction_destination
  from src
),

derived as (
  select
    *,
    case
      when lower(direction) in ('inbound', 'in') then 'Inbound'
      when lower(direction) in ('outbound', 'out') then 'Outbound'
      else direction
    end as direction_label,

    lower(regexp_replace(coalesce(direction_destination, ''), '[^a-zA-Z0-9 ]', ' ', 'g')) as destination_search
  from clean
)

select * from derived;