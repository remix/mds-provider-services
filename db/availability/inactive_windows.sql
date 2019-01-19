-- Windows of time a given provider's device was marked as available for rental

DROP VIEW IF EXISTS public.inactive_windows_all_from_events CASCADE;

CREATE VIEW public.inactive_windows_all_from_events AS

SELECT
    avail.provider_id as provider_id,
    avail.device_id as device_id,
    avail.event_location AS event_location,
    avail.event_type AS start_event_type,
    notavail.event_type AS end_event_type,
    avail.event_type_reason AS start_reason,
    notavail.event_type_reason AS end_reason,
    avail.event_time AS start_time,
    notavail.event_time AS end_time
FROM
    device_event_timeline_dedupe_all avail LEFT JOIN device_event_timeline_dedupe_all notavail
    ON (avail.event_type = 'available' or avail.event_type = 'reserved')
    AND notavail.event_type <> 'available'
    AND avail.provider_id = notavail.provider_id
    AND avail.device_id = notavail.device_id
    AND (avail.row_num + 1) = notavail.row_num
WHERE
    (avail.event_type = 'available' or avail.event_type = 'reserved')

;
