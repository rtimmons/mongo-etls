"""
By convention we expose the _DAG object in a __mars__.py file.
"""

from datetime import datetime, timedelta

from src.jobs.parser import parse_job_config
from src.jobs.variable import get_mars_var
from src.jobs.whereami import repo_path

_DAG = parse_job_config(
    repo_path(
        "src", "jobs", "dev_prod", "materialize_historical_test_data", "job_config.jinja.json"
    ),
    {
        "presto_conn_id": get_mars_var("presto_conn_id"),
        "github_conn_id": get_mars_var("github_conn_id"),
        "mdb_conn_id": get_mars_var("mdb_conn_id"),
        "environment": get_mars_var("environment"),
        "date": f"{datetime.now().date() - timedelta(days=1)}",
    },
)
