--
-- Target:
-- awsdatacatalog.dev_prod_live.cedar_perf_results_src
--

SELECT  rs."_id"        AS "_id",
        *,
        LOCALTIMESTAMP  AS _extract_timestamp
FROM    evergreen_cedar_atlas.cedar.perf_results AS rs
