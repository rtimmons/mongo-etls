--
-- Target: awsdatacatalog.dev_prod_live.performance_expanded_metrics_change_points_src
--

SELECT  *,
        localtimestamp as _extract_timestamp
FROM    dev_prod_performance_atlas.expanded_metrics.change_points
