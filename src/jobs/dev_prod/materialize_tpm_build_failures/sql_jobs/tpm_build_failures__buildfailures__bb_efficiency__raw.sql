-- This file generated by generate.py.

-- <yaml>
-- DependsOn: {}
-- </yaml>
SELECT  CAST(vs."_id" AS VARCHAR)       AS "_id",
        vs."bfgscreated"                AS "bfgscreated",
        vs."bfgsresolved"               AS "bfgsresolved",
        vs."bfgsresolvedautomatically"  AS "bfgsresolvedautomatically",
        vs."bfgsresolvedbyperson"       AS "bfgsresolvedbyperson",
        vs."enddate"                    AS "enddate",
        vs."startdate"                  AS "startdate"
        -- <COMMON_ETL_FIELDS>
        , LOCALTIMESTAMP AS "_extract_timestamp"
        -- </COMMON_ETL_FIELDS>
FROM  "tpm_build_failures_atlas"."buildfailures"."bb_efficiency" AS vs

