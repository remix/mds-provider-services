CREATE TABLE status_changes (
    provider_id UUID NOT NULL,
    provider_name TEXT NOT NULL,
    device_id UUID NOT NULL,
    vehicle_id TEXT NOT NULL,
    vehicle_type vehicle_types NOT NULL,
    propulsion_type propulsion_types[] NOT NULL,
    event_type event_types NOT NULL,
    event_type_reason event_type_reasons NOT NULL,
    event_time timestamptz NOT NULL,
    event_location jsonb NOT NULL,
    battery_pct FLOAT,
    associated_trips UUID[]
);

ALTER TABLE status_changes
    ADD CONSTRAINT unique_event
    UNIQUE (provider_id,
            device_id,
            event_type,
            event_type_reason,
            event_time
    );