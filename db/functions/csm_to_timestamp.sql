-- double -> timestamptz
CREATE OR REPLACE FUNCTION csm_to_timestamp(double precision)
    RETURNS timestamptz
    LANGUAGE sql
    STABLE
AS $BODY$
    SELECT
        CASE
            WHEN to_timestamp($1) > now() THEN
                to_timestamp($1 / 1000.0)
            ELSE
                to_timestamp($1)
        END;
$BODY$;