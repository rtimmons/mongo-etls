"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from src.jobs.helpers import DagHelper

_HELPER = DagHelper(__file__)

tpm_build_failures__buildfailures__bb_efficiency__raw = _HELPER.add_task(
    "tpm_build_failures__buildfailures__bb_efficiency__raw"
)
tpm_build_failures__buildfailures__bf__raw = _HELPER.add_task(
    "tpm_build_failures__buildfailures__bf__raw"
)
tpm_build_failures__buildfailures__durations__raw = _HELPER.add_task(
    "tpm_build_failures__buildfailures__durations__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__compile_tasks__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__compile_tasks__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__completed_versions__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__completed_versions__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__ignored_versions__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__ignored_versions__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__query_patch_completed_versions__raw = (
    _HELPER.add_task(
        "tpm_build_failures__coredb-patchbuild-optimizer__query_patch_completed_versions__raw"
    )
)
tpm_build_failures__coredb_patchbuild_optimizer__query_patch_ignored_versions__raw = (
    _HELPER.add_task(
        "tpm_build_failures__coredb-patchbuild-optimizer__query_patch_ignored_versions__raw"
    )
)
tpm_build_failures__coredb_patchbuild_optimizer__query_patch_version_build_variant_data__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__query_patch_version_build_variant_data__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__query_patch_version_task_data__raw = (
    _HELPER.add_task(
        "tpm_build_failures__coredb-patchbuild-optimizer__query_patch_version_task_data__raw"
    )
)
tpm_build_failures__coredb_patchbuild_optimizer__query_patch_version_test_data__raw = (
    _HELPER.add_task(
        "tpm_build_failures__coredb-patchbuild-optimizer__query_patch_version_test_data__raw"
    )
)
tpm_build_failures__coredb_patchbuild_optimizer__query_patch_versions_to_retry__raw = (
    _HELPER.add_task(
        "tpm_build_failures__coredb-patchbuild-optimizer__query_patch_versions_to_retry__raw"
    )
)
tpm_build_failures__coredb_patchbuild_optimizer__recently_changed_test_data__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__recently_changed_test_data__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__server_data__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__server_data__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__status_config__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__status_config__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__version_test_data__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__version_test_data__raw"
)
tpm_build_failures__coredb_patchbuild_optimizer__versions_to_retry__raw = _HELPER.add_task(
    "tpm_build_failures__coredb-patchbuild-optimizer__versions_to_retry__raw"
)
tpm_build_failures__data__task_stats__raw = _HELPER.add_task(
    "tpm_build_failures__data__task_stats__raw"
)

_DAG = _HELPER.extract()
