-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."average_duration"      AS "average_duration",
        vs."info"                  AS "info",
        vs."last_update"           AS "last_update",
        vs."num_pass"              AS "num_pass"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  evergreen_cedar_atlas.cedar.historical_test_data AS vs

