"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.model import DagHelper

_HELPER = DagHelper(__file__)

build_baron__auto_revert__failed_tasks__raw = _HELPER.add_task(
    "build_baron__auto_revert__failed_tasks__raw"
)
build_baron__auto_revert__revert_candidates__raw = _HELPER.add_task(
    "build_baron__auto_revert__revert_candidates__raw"
)
build_baron__auto_revert__reverts__raw = _HELPER.add_task("build_baron__auto_revert__reverts__raw")
build_baron__buildbaron__auto_resolution_rules__raw = _HELPER.add_task(
    "build_baron__buildbaron__auto_resolution_rules__raw"
)
build_baron__buildbaron__bfg_context_attributes__raw = _HELPER.add_task(
    "build_baron__buildbaron__bfg_context_attributes__raw"
)
build_baron__buildbaron__bfg_contexts__raw = _HELPER.add_task(
    "build_baron__buildbaron__bfg_contexts__raw"
)
build_baron__buildbaron__bfg_contexts_audit__raw = _HELPER.add_task(
    "build_baron__buildbaron__bfg_contexts_audit__raw"
)
build_baron__buildbaron__bfg_key__raw = _HELPER.add_task("build_baron__buildbaron__bfg_key__raw")
build_baron__buildbaron__bfgs__raw = _HELPER.add_task("build_baron__buildbaron__bfgs__raw")
build_baron__buildbaron__bfs__raw = _HELPER.add_task("build_baron__buildbaron__bfs__raw")
build_baron__buildbaron__patch_failures__raw = _HELPER.add_task(
    "build_baron__buildbaron__patch_failures__raw"
)

_DAG = _HELPER.extract()
