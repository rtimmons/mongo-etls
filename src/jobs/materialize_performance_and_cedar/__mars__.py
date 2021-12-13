"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from jobs.helpers import DagHelper

helper = DagHelper(__file__)

perf_results = helper.add_task("perf_results")
perf_results_unrolled = helper.add_task("perf_results_unrolled")
perf_results_unrolled.set_prev(perf_results)

time_series = helper.add_task("time_series")
time_series_unrolled = helper.add_task("time_series_unrolled")
time_series_unrolled.set_prev(time_series)

_DAG = helper.extract()
