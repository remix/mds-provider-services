-- A de-deduplicated device event timeline

DROP VIEW IF EXISTS public.device_event_timeline_dedupe_all CASCADE;

CREATE VIEW public.device_event_timeline_dedupe_all AS

SELECT
    *,
    row_number() OVER (order by provider_id, device_id, event_time) AS row_num
FROM
    (SELECT -- the non-duplicated records
        provider_id,
        device_id,
        event_type,
        event_type_reason,
        event_time,
        event_location,
        associated_trips
        FROM
            (SELECT -- the duplicate records
                _left.provider_id,
                _left.device_id,
                _left.event_type,
                _left.event_type_reason,
                _left.event_time,
                _left.location AS event_location,
                _left.associated_trips,
                _left.row_num,
                _right.row_num IS NULL AS condition
            FROM
                -- join with self, for each provider's device
                device_event_timeline_all _left LEFT JOIN device_event_timeline_all _right
                ON _left.provider_id = _right.provider_id
                AND _left.device_id = _right.device_id
                -- the next row, e.g. the next event in the timeline for this provider's device
                AND (_left.row_num + 1) = _right.row_num
                -- both 'available' -> user/data/transmission error
                AND ((_left.event_type = 'available' AND _right.event_type = 'available') OR
                -- both the same, not 'avail' ->
                    (_left.event_type <> 'available' AND _right.event_type <> 'available'))
        ) dupe
        WHERE
            dupe.condition
    ) no_dupe

;
