"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.model import DagHelper

_HELPER = DagHelper(__file__)

performance__expanded_metrics__change_points__raw = _HELPER.add_task(
    "performance__expanded_metrics__change_points__raw"
)

performance__expanded_metrics__time_series__raw = _HELPER.add_task(
    "performance__expanded_metrics__time_series__raw"
)
performance__expanded_metrics__time_series_unrolled_intermediate = _HELPER.add_task(
    "performance__expanded_metrics__time_series_unrolled_intermediate"
)
performance__expanded_metrics__time_series_unrolled_intermediate.set_prev(
    performance__expanded_metrics__time_series__raw
)

performance__expanded_metrics__versions__raw = _HELPER.add_task(
    "performance__expanded_metrics__versions__raw"
)


_DAG = _HELPER.extract()

##
# TODO: Add automated testing to ensure we can
#       do the below for all _DAG objects.
#
# import json
# assert(_DAG.is_valid())
# json.dumps(_DAG.to_payload())
#
##
