"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.helpers import DagHelper

helper = DagHelper(__file__)


cedar__cedar__perf_results__raw = helper.add_task("cedar__cedar__perf_results__raw")
cedar__cedar__perf_results__raw__unrolled = helper.add_task(
    "cedar__cedar__perf_results__raw__unrolled"
)
cedar__cedar__perf_results__raw__unrolled.set_prev(cedar__cedar__perf_results__raw)

cedar__cedar__test_results__raw = helper.add_task("cedar__cedar__test_results__raw")

performance__expanded_metrics__change_points__raw = helper.add_task(
    "performance__expanded_metrics__change_points__raw"
)

performance__expanded_metrics__time_series__raw = helper.add_task(
    "performance__expanded_metrics__time_series__raw"
)
performance__expanded_metrics__time_series__raw__unrolled = helper.add_task(
    "performance__expanded_metrics__time_series__raw__unrolled"
)
performance__expanded_metrics__time_series__raw__unrolled.set_prev(
    performance__expanded_metrics__time_series__raw
)

performance__expanded_metrics__versions__raw = helper.add_task(
    "performance__expanded_metrics__versions__raw"
)


_DAG = helper.extract()
