-- Each event, for each device, for each provider - ordered chronologically

DROP VIEW IF EXISTS public.device_event_timeline CASCADE;

CREATE VIEW public.device_event_timeline AS

SELECT
    row_number() OVER (ORDER BY provider_id, device_id, event_time) AS row_num,
    *
FROM
    events
WHERE
    org_id = 11
ORDER BY
    provider_id,
    row_num

;
