--
-- Target: awsdatacatalog.dev_prod_live.performance_expanded_metrics_change_points_src
--

SELECT  *,
        LOCALTIMESTAMP AS _extract_timestamp
FROM    dev_prod_performance_atlas.expanded_metrics.time_series
