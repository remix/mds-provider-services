-- Windows of time a given provider's device was active in a trip

DROP VIEW IF EXISTS public.active_windows_all_from_events CASCADE;

CREATE VIEW public.active_windows_all_from_events AS

SELECT
    pickup.provider_id,
    pickup.device_id,
    pickup.location AS event_location,
    pickup.event_type AS start_event_type,
    next_event.event_type AS end_event_type,
    pickup.event_type_reason AS start_reason,
    next_event.event_type_reason AS end_reason,
    pickup.event_time AS start_time,
    next_event.event_time AS end_time
FROM
    device_event_timeline_all pickup LEFT JOIN device_event_timeline_all next_event
    ON pickup.event_type_reason = 'user_pick_up'
    AND pickup.provider_id = next_event.provider_id
    AND pickup.device_id = next_event.device_id
    AND (pickup.row_num + 1) = next_event.row_num
WHERE
    pickup.event_type_reason = 'user_pick_up'
;