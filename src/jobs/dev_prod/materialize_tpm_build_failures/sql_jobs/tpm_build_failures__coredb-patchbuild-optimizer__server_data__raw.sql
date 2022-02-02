-- NOTE:
-- The "_options" and "fields" columns cause Presto to barf
-- with a cryptic error message.
--   SQL Error [65542]: Query failed (#20220124_172159_07498_x5ks9): Unexpected response from http://100.104.64.3:8080/v1/task/20220124_172159_07498_x5ks9.1.13?summarize

-- I (ryan.timmmons) tried to export the data to local files. This works fine in DBeaver.
-- I suspect there are a few rows (docs) that don't follow the schema or perhaps the schema
-- is incorrect. It was auto-generated and may not account for some sparsely-populated fields.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."_base_url"             AS "_base_url",
        -- vs."_options"              AS "_options",
        vs."_resource"             AS "_resource",
        vs."expand"                AS "expand",
        -- vs."fields"                AS "fields",
        vs."histories"             AS "histories",
        vs."id"                    AS "id",
        vs."key"                   AS "key",
        vs."self"                  AS "self"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "tpm_build_failures_atlas"."coredb-patchbuild-optimizer"."server_data" AS vs

