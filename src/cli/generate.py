"""
Generates canonical SQL files given a structure.yml file in a job directory.

    ./ci.sh python3 src/cli/generate.py materialize_performance_and_cedar

Reads structure.yml and generates select statement files in sql_jobs.
"""
import os
import os.path
import sys
from typing import List

import yaml

import src.jobs.whereami as whereami


def _get_struct(job_name: str) -> dict:
    struct_path = whereami.repo_path("src", "jobs", job_name, "structure.yml")
    with open(struct_path, "r") as handle:
        return yaml.safe_load(handle)


_DEFAULT_SUFFIXES = {
    "COMMON_ETL_FIELDS": ', LOCALTIMESTAMP AS "_extract_timestamp"',
}


def _select_statement(
    kvs: dict, padding: int = 2, leader: str = "SELECT", suffixes: dict = None
) -> str:
    max_len = 0
    for k in kvs.keys():
        max_len = max(max_len, len(k))

    leader_len = len(leader)

    out = []
    count = -1
    max_count = len(kvs.keys()) - 1
    for k, v in kvs.items():
        count += 1
        if count == 0:
            line = f"{leader}{' '*padding}"
        else:
            line = f"{' '*(leader_len+padding)}"
        remain = max_len - len(k) + padding
        line = f"{line}{k}{' '*remain}AS {v}"
        if count < max_count:
            line = f"{line},"
        out.append(line)

    # Suffix handling
    if suffixes is None:
        suffixes = _DEFAULT_SUFFIXES
    for name, suffix in suffixes.items():
        out.append(f"{' '*(leader_len+padding)}-- <{name}>")
        suffix_lines = suffix.split("\n")
        for suffix_line in suffix_lines:
            out.append(f"{' ' * (leader_len + padding)}{suffix_line}")
        out.append(f"{' ' * (leader_len + padding)}-- </{name}>")

    return "\n".join(out)


_TO_REMOVE = {"dev_prod_", "_atlas", "evergreen_"}


_GENERATED_PREFIX = "-- This file generated by generate.py."


def _main(argv: List[str]) -> None:
    job_name = argv[1]
    struct = _get_struct(job_name)
    for source_name, source in struct["Sources"].items():
        for db_name, db in source.items():
            for table_name, table in db.items():
                col_dict = dict()
                col_dict['CAST(vs."_id" AS VARCHAR)'] = '"_id"'
                for column in table:
                    if column == "_id":
                        continue
                    col_dict[f'vs."{column}"'] = f'"{column}"'

                select_st = _select_statement(col_dict)
                from_st = f'FROM  "{source_name}"."{db_name}"."{table_name}" AS vs'
                prefix = f"{_GENERATED_PREFIX}\n\n-- <yaml>\n-- DependsOn: " + "{}\n-- </yaml>"
                contents = f"{prefix}\n{select_st}\n{from_st}\n\n"

                file_name = f"{source_name}__{db_name}__{table_name}__raw.sql"
                for removal in _TO_REMOVE:
                    file_name = file_name.replace(removal, "")

                cwd = os.getcwd()
                try:
                    path = os.path.join(
                        os.path.dirname(__file__), "..", "jobs", job_name, "sql_jobs"
                    )
                    os.chdir(path)
                    if os.path.exists(file_name):
                        with open(file_name, "r") as handle:
                            first = handle.readline().strip()
                            if first != _GENERATED_PREFIX:
                                print(f"Skipping {file_name} since not generated.")
                                continue
                    with open(file_name, "w") as handle:
                        handle.write(contents)
                finally:
                    os.chdir(cwd)


if __name__ == "__main__":
    _main(sys.argv)
