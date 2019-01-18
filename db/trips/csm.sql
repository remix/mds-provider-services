DROP VIEW IF EXISTS public.csm_trips CASCADE;

CREATE VIEW public.csm_trips AS

SELECT
    trips.provider_id,
    trips.device_id,
    trips.trip_id,
    trips.start_time,
    trips.end_time,
    --csm_routes.first_csm_time,
    extract(epoch from trips.start_time) as first_csm_time,
    --csm_routes.last_csm_time,
    extract(epoch from trips.end_time) as last_csm_time,
    --csm_routes.first_csm_point
    ST_SETSRID(ST_GeomFromGeoJSON(route_geojson->'features'->0->>'geometry'), 4326) as first_csm_point
FROM
    trips
WHERE
    org_id = 11
;
