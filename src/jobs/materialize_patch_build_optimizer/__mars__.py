"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.dag_helper import DagHelper

_HELPER = DagHelper(__file__)

patch_build_optimizer__evg__completed_versions__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__completed_versions__raw"
)
patch_build_optimizer__evg__ignored_versions__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__ignored_versions__raw"
)
patch_build_optimizer__evg__query_patch_completed_versions__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__query_patch_completed_versions__raw"
)
patch_build_optimizer__evg__query_patch_ignored_versions__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__query_patch_ignored_versions__raw"
)
patch_build_optimizer__evg__query_patch_version_build_variant_data__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__query_patch_version_build_variant_data__raw"
)
patch_build_optimizer__evg__query_patch_version_task_data__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__query_patch_version_task_data__raw"
)
patch_build_optimizer__evg__query_patch_version_test_data__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__query_patch_version_test_data__raw"
)
patch_build_optimizer__evg__query_patch_versions_to_retry__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__query_patch_versions_to_retry__raw"
)
patch_build_optimizer__evg__version_test_data__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__version_test_data__raw"
)
patch_build_optimizer__evg__versions_to_retry__raw = _HELPER.add_task(
    "patch_build_optimizer__evg__versions_to_retry__raw"
)
patch_build_optimizer__jira__bf_data__raw = _HELPER.add_task(
    "patch_build_optimizer__jira__bf_data__raw"
)
patch_build_optimizer__symbols_staging__mappings__raw = _HELPER.add_task(
    "patch_build_optimizer__symbols-staging__mappings__raw"
)
patch_build_optimizer__symbols__mappings__raw = _HELPER.add_task(
    "patch_build_optimizer__symbols__mappings__raw"
)


_DAG = _HELPER.extract()
