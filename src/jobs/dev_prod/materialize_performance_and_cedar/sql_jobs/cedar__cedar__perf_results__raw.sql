-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."analysis"              AS "analysis",
        vs."completed_at"          AS "completed_at",
        vs."created_at"            AS "created_at",
        vs."info"                  AS "info",
        vs."rollups"               AS "rollups"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "evergreen_cedar_atlas"."cedar"."perf_results" AS vs

