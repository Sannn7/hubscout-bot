{{ config(materialized='table', schema='raw_main_staging') }}

with src as (
  select * from {{ source('raw', 'gtfs_checkpoints') }}
),

clean as (
  select
    cast(checkpoint_id as varchar) as checkpoint_id,
    nullif(trim(cast(checkpoint_name as varchar)), '') as checkpoint_name
  from src
),

derived as (
  select
    *,
    lower(regexp_replace(coalesce(checkpoint_name, ''), '[^a-zA-Z0-9 ]', ' ', 'g')) as checkpoint_name_search,
    trim(regexp_replace(coalesce(checkpoint_name, ''), '\s+', ' ', 'g')) as checkpoint_name_clean
  from clean
)

select * from derived;