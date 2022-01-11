-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."artifact"              AS "artifact",
        vs."completed_at"          AS "completed_at",
        vs."created_at"            AS "created_at",
        vs."info"                  AS "info"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  evergreen_cedar_atlas.cedar.buildlogs AS vs

