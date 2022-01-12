"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.helpers import DagHelper

_HELPER = DagHelper(__file__)

# TODO

_DAG = _HELPER.extract()
