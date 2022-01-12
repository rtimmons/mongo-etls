-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."arch"                  AS "arch",
        vs."binary_name"           AS "binary_name",
        vs."build_id"              AS "build_id",
        vs."debug_symbols_url"     AS "debug_symbols_url",
        vs."edition"               AS "edition",
        vs."sha256"                AS "sha256",
        vs."target"                AS "target",
        vs."url"                   AS "url",
        vs."version"               AS "version"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  patch_build_optimizer_atlas.symbols-staging.mappings AS vs

