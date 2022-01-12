import importlib
import os
import os.path
import tempfile
import unittest
from typing import Any

from src.jobs import whereami


# Copied loosely from
# https://github.com/10gen/mars/blob/95aa3afa31ae5abc448c8535a78a4461d078d6bd/mars-worker/dag_render_main.py#L46
def import_github_package(folder: str, entry_point: str) -> Any:
    """Imports a DAG package fetched from Github

    Args:
        folder: name of the DAG folder where package is cloned into
        entry_point: relative path to the DAG file to import

    Returns:
        DAG object exported by the package
    """
    dag_pkg = folder
    if dag_pkg[-1] == "/":
        dag_pkg = dag_pkg[:-1]

    dir_path, file = os.path.split(entry_point)
    file = file.split(".")[0]
    to_import = f"{dag_pkg}.{os.path.join(dir_path, file).replace('/', '.')}"
    m = importlib.import_module(to_import)
    return m._DAG


_FOLDER_NAME = "dag_pkg"


def run_entry_point(entry_point: str) -> Any:
    repo_root = whereami.repo_path()
    cwd = os.getcwd()
    try:
        # TODO: this requires "ln -s $PWD dag_pkg" for some reason
        with tempfile.TemporaryDirectory() as tmpdirname:
            os.chdir(tmpdirname)
            os.symlink(repo_root, _FOLDER_NAME)
            return import_github_package(folder=_FOLDER_NAME, entry_point=entry_point)
    finally:
        os.chdir(cwd)


class EntryPointsTests(unittest.TestCase):
    def test_jobs_mars_imports(self):
        root_path = whereami.repo_path("src", "jobs")  # /home/foo/Projects/mongo-etls/src/jobs
        found = 0
        for ent in os.listdir(root_path):  # ent like "materialize_large_cedar" and "whereami.py"
            ent_path = os.path.join(root_path, ent)
            mars_path = os.path.join(
                "src", "jobs", ent, "__mars__.py"
            )  # src/jobs/materialize_foo/__mars__.py
            full_mars_path = os.path.join(ent_path, "__mars__.py")
            if os.path.isdir(ent_path) and os.path.exists(full_mars_path):
                the_dag = run_entry_point(mars_path)
                self.assertIsNotNone(the_dag, f"Job {ent} not exported properly")
                found += 1

        # Basic sanity check that we found at least two jobs.
        # Consider bumping this as more jobs are added
        # or if the above logic is changed in any real way.
        self.assertGreaterEqual(found, 3)
