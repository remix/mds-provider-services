-- Windows of time a given provider's device was in the public right-of-way

DROP VIEW IF EXISTS public.csm_availability_all_from_trips CASCADE;

CREATE VIEW public.csm_availability_all_from_trips AS

SELECT
    provider_id,
    device_id,
    start_event_type,
    start_reason,
    end_event_type,
    end_reason,
    start_time,
    end_time,
    event_location
FROM
    public.availability_all_from_trips
ORDER BY
    (start_time, end_time)

;
