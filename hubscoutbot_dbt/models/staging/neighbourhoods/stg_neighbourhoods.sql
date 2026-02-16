{{ config(materialized='table', schema='main_staging') }}

select
  cast(attributes.neighborhood_id as varchar) as neighbourhood_id,
  cast(attributes.name as varchar)            as neighbourhood_name,
  cast(attributes.acres as double)            as acres,
  cast(attributes.sqmiles as double)          as sq_miles,
  cast(attributes.objectid as bigint)         as object_id,

  cast(attributes."SHAPE__Area" as double)    as shape_area,
  cast(attributes."SHAPE__Length" as double)  as shape_length,

  geometry,
  source,
  ingested_at
from {{ source('raw', 'neighbourhoods') }}