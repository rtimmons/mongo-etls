import importlib
import os
import sys

# TODO: link to relevant mars code
# TODO: move to a CI test


def import_github_package(folder: str, entry_point: str):
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
    print(f"import {to_import}")
    m = importlib.import_module(to_import)
    return m._DAG


if __name__ == "__main__":
    # TODO: requires `ln -s $PWD some_checkout_dir` and then invoked with that as argv[1].
    #    ln -s $PWD ./dag_pkg
    #    python mars_entry_point.py dag_pkg/
    ENTRY_POINT = "src/jobs/materialize_large_cedar/__mars__.py"
    print(f"argv={sys.argv}")
    dag = import_github_package(folder=sys.argv[1], entry_point=ENTRY_POINT)
    print(f"_DAG=[{dag}]")

