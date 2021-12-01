import os.path

from mars_util.job_dag import JobDAG
from mars_util.task import PrestoTask
from mars_util.task.destination import PrestoTableDestination

dag = JobDAG()

PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"


def read_file(*relative_to_self):
    mydir = os.path.dirname(__file__)
    to_read = os.path.join(mydir, *relative_to_self)
    with open(to_read) as handle:
        return handle.read()

task_1 = PrestoTask(
    name="materialize dev_prod_performance_atlas.evgdw.build_failures",
    conn_id="2cc4534c-7634-433f-8e01-8fb0ad19e282",
    sql_source="config",
    sql=read_file("../../src/jobs/peformance_pipeline/cedar_perf_results_src/index.sql"),
    destination=PrestoTableDestination(
        dest_tgt="awsdatacatalog.dev_prod_live.performance_evgdw_build_vailures",
        dest_replace=True,
        dest_format="table",
    )
)

dag.register_tasks([task_1])

_DAG = dag

