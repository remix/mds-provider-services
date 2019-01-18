-- Each event, for each device, for each provider - ordered chronologically

DROP VIEW IF EXISTS public.device_event_timeline_all CASCADE;

CREATE VIEW public.device_event_timeline_all AS

SELECT
    row_number() OVER (ORDER BY provider_id, device_id, event_time) AS row_num,
    *
FROM
    events
WHERE
    org_id = 11
--AND ST_Intersects(csm_city_boundary(), location)
ORDER BY
    provider_id,
    row_num

;
