-- Windows of time a given provider's device was in the public right-of-way

DROP VIEW IF EXISTS public.availability_inside_from_trips CASCADE;

CREATE VIEW public.availability_inside_from_trips AS

SELECT
    provider_id,
    device_id,
    event_location,
    start_event_type,
    end_event_type,
    start_reason,
    end_reason,
    start_time,
    end_time
FROM
    inactive_windows_inside_from_trips

UNION

SELECT
    provider_id,
    device_id,
    event_location,
    start_event_type,
    end_event_type,
    start_reason,
    end_reason,
    start_time,
    end_time
FROM
    active_windows_inside

;
