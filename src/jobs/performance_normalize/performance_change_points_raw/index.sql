--
-- target: awsdatacatalog.dev_prod_live.performance_expanded_metrics_change_points
-- 

select 	time_series_info.project as "project",
		time_series_info.variant as "variant",
		time_series_info.task as "task",
		time_series_info.test as "test",
		time_series_info.measurement as "measurement",
		version,
		if(
			   time_series_info.test like '%canary%'
			or time_series_info.test like '%fio%'
			or time_series_info.test like '%NetworkB%'
			or time_series_info.test like '%Setup%'
			or time_series_info.test like '%CleanUp%'
			or time_series_info.test like '%ActorStarted%'
			or time_series_info.test like '%ActorFinished%',
			'yes', 'no'
		)
		test_matches_canary_rex,
		date(triage.triaged_on) as triaged_on,
		triage.triage_status as triage_status,
		date(calculated_on) as calculated_on
from 	dev_prod_performance_atlas.expanded_metrics.change_points
where 	calculated_on between date('2012-09-16') and date(now())
