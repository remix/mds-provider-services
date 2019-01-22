DROP VIEW IF EXISTS public.csm_trips CASCADE;

CREATE VIEW public.csm_trips AS

SELECT
    trips.provider_id,
    trips.device_id,
    trips.trip_id,
    trips.start_time,
    trips.end_time,
    csm_routes.first_csm_time,
    csm_routes.last_csm_time,
    csm_routes.first_csm_point
FROM
    trips INNER JOIN csm_routes
        ON trips.org_id = 11
        AND trips.provider_id = csm_routes.provider_id
        AND trips.trip_id = csm_routes.trip_id

;
