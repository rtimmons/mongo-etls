-- <yaml>
-- DependsOn: {}
-- </yaml>

-- Note:
-- The source data is very large (hundreds of GiB) so the Presto task
-- with this un-optimized query times out after a few hours. The "correct"
-- solution is to do a delta/insertion query here but that requires some
-- development effort that needs to be prioritized by the owners of the data.


SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."average_duration"      AS "average_duration",
        vs."info"                  AS "info",
        vs."last_update"           AS "last_update",
        vs."num_pass"              AS "num_pass",
       'SAMPLE DATA DONT USE ME'   AS _commentary
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "evergreen_cedar_atlas"."cedar"."historical_test_data" AS vs
LIMIT 10000
