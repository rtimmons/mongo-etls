from mars_util.task import PrestoTask
from mars_util.task.destination import PrestoTableDestination

import os.path

import jobs.whereami

PRESTO_CONN = "920d5dfe-33ba-402a-b3ed-67ba21c25582"


def read_file(*repo_rooted_path):
    to_read = jobs.whereami.repo_path(*repo_rooted_path)
    with open(to_read) as handle:
        return handle.read()


class ConventionalPrestoTask(PrestoTask):
    def __init__(self, name: str, file_path: str, **other_args):
        args = {
            "name": name,
            "conn_id": PRESTO_CONN,
            "sql_source": "config",
            "destination": PrestoTableDestination(
                dest_tgt=f"awsdatacatalog.dev_prod_live.{name}",
                dest_replace=True,
                dest_format="table",
            ),
        }
        if "sql" not in other_args:
            args["sql"] = read_file(os.path.dirname(file_path), f"{name}.sql")
        args.update(other_args)
        super().__init__(**args)
