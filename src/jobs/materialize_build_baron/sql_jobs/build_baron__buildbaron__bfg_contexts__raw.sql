-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)  AS "_id",
        vs."name"                  AS "name",
        vs."priority"              AS "priority",
        vs."rules"                 AS "rules"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  dev_prod_build_baron_atlas.buildbaron.bfg_contexts AS vs

