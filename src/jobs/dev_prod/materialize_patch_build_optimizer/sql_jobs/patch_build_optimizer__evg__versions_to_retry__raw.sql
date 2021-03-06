-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)   AS "_id",
        vs."api_version"            AS "api_version",
        vs."author"                 AS "author",
        vs."author_email"           AS "author_email",
        vs."branch"                 AS "branch",
        vs."build_variants_status"  AS "build_variants_status",
        vs."create_time"            AS "create_time",
        vs."finish_time"            AS "finish_time",
        vs."message"                AS "message",
        vs."order"                  AS "order",
        vs."project"                AS "project",
        vs."project_identifier"     AS "project_identifier",
        vs."repo"                   AS "repo",
        vs."requester"              AS "requester",
        vs."revision"               AS "revision",
        vs."start_time"             AS "start_time",
        vs."status"                 AS "status",
        vs."version_id"             AS "version_id"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "patch_build_optimizer_atlas"."evg"."versions_to_retry" AS vs

