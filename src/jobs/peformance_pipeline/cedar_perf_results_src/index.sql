--
-- Target:
-- awsdatacatalog.dev_prod_live.cedar_perf_results_src
--

SELECT  *,
        localtimestamp as _extract_timestamp
FROM    evergreen_cedar_atlas.cedar.perf_results
