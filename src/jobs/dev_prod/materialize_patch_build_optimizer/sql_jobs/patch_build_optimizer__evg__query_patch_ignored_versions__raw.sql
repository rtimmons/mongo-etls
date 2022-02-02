-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."api_version"           AS "api_version",
        vs."reason"                AS "reason",
        vs."version_id"            AS "version_id"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "patch_build_optimizer_atlas"."evg"."query_patch_ignored_versions" AS vs

