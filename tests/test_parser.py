import json
import os
import unittest

import src.jobs.parser as parser
from src.jobs.whereami import repo_path

_valid_job_config = [
    {
        "name": "task0",
        "type": "presto",
        "conn_id": "[@dag-eval presto_conn_id @]",
        "sql_source": "github",
        "sql_script_conn": "[@dag-eval github_conn_id @]",
        "sql_script_git_repo": "10gen/some-repo",
        "sql_script_name": "some-dir/some-file",
        "sql_script_git_branch": "main",
        "children": {"task1": "on_success", "task3": "on_failure"},
    },
    {
        "name": "task1",
        "type": "presto",
        "conn_id": "[@dag-eval presto_conn_id @]",
        "destination": {
            "type": "mongodb",
            "dest_mdb_database": "db",
            "dest_mdb_collection": "coll",
            "dest_mdb_conn_info": "[@dag-eval mdb_conn_id @]",
            "dest_mdb_op": "insert",
        },
        "sql_source": "github",
        "sql_script_conn": "[@dag-eval github_conn_id @]",
        "sql_script_git_repo": "10gen/some-repo",
        "sql_script_name": "some-other-dir/some-other-file",
        "sql_script_git_branch": "main",
        "children": {"task2": "on_completion", "task3": "on_failure"},
    },
    {
        "name": "task2",
        "type": "mongodb",
        "conn_id": "[@dag-eval mdb_conn_id @]",
        "op": "update",
        "database": "db",
        "collection": "coll",
        "update_condition": {"some_field": "some_value"},
        "update_op": {"$set": {"some_other_field": "some_other_value"}},
        "children": {"task3": "on_failure"},
    },
    {
        "name": "task3",
        "type": "alert",
        "conn_id": "[@dag-eval splunk_conn_id @]",
        "alert_type": "slack",
        "sender": "some-sender",
        "target": "some-channel",
        "title": "Something Failed",
        "msg": "Some message.",
    },
]

_invalid_job_config = [
    {
        "name": "task0",
        "type": "presto",
        "conn_id": "[@dag-eval presto_conn_id @]",
        "sql_source": "github",
        "sql_script_conn": "[@dag-eval github_conn_id @]",
        "sql_script_git_repo": "10gen/some-repo",
        "sql_script_name": "some-dir/some-file",
        "sql_script_git_branch": "main",
        "children": {"task1": "on_success"},
    },
    {
        "name": "task1",
        "type": "mongodb",
        "conn_id": "[@dag-eval mdb_conn_id @]",
        "op": "update",
        "database": "db",
        "collection": "coll",
        "update_condition": {"some_field": "some_value"},
        "update_op": {"$set": {"some_other_field": "some_other_value"}},
        "children": {"task0": "on_success"},
    },
]


class TestParserTests(unittest.TestCase):
    valid_config_filename = "valid_job_config.jinja.json"
    invalid_config_filename = "invalid_job_config.jinja.json"

    def setUp(self):
        with open(self.valid_config_filename, "w") as f:
            f.write(json.dumps(_valid_job_config))

        with open(self.invalid_config_filename, "w") as f:
            f.write(json.dumps(_invalid_job_config))

    def tearDown(self):
        try:
            os.remove(self.valid_config_filename)
        except FileNotFoundError:
            pass

        try:
            os.remove(self.invalid_config_filename)
        except FileNotFoundError:
            pass

    def test_parses_valid_config(self):
        generated_dag = parser.parse_job_config(
            repo_path(self.valid_config_filename),
            {
                "presto_conn_id": "presto_id",
                "github_conn_id": "github_id",
                "mdb_conn_id": "mongo_id",
            },
        )

        self.assertEqual(len(generated_dag._tasks), len(_valid_job_config))

        task_map = {}
        for t in generated_dag._tasks.values():
            task_map[t.name] = t

        for task_config in _valid_job_config:
            self.assertTrue(task_config["name"] in task_map)
            t = task_map[task_config["name"]]
            self.assertEqual(task_config["type"], t.TASK_TYPE)

            if "destination" in task_config:
                dest_config = task_config["destination"]
                self.assertEqual(
                    type(parser._destinations[dest_config["type"]](**dest_config)),
                    type(t._destination),
                )

            if "children" in task_config:
                children = task_config["children"]
                self.assertEqual(len(children), len(t.edges))
                for edge in t.edges:
                    self.assertTrue(edge.to_ref.name in children)

                    condition = parser._conditions[children[edge.to_ref.name]]
                    self.assertEqual(condition, edge._cond)

    def test_fails_with_invalid_job_dag(self):
        self.assertRaises(
            ValueError,
            parser.parse_job_config,
            repo_path(self.invalid_config_filename),
            {
                "presto_conn_id": "presto_id",
                "github_conn_id": "github_id",
                "mdb_conn_id": "mongo_id",
            },
        )
