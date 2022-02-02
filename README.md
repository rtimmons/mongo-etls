# R&D Dev-Prod ETLs

This repository contains all the ETLs that comprise the R&D Dev-Prod data pipeline. This pipeline runs on MARS and interacts with Presto and other data-sources.

```sh
git clone git@github.com:10gen/dev-prod-etls.git
cd dev-prod-etls
./ci.sh pytest
```

## Data Pipeline Components

When creating new jobs or components of the data-pipeline, please refer to the [Policies](./docs/policies.md) before sending PRs.

## Note on the `dag_pkg` symlink

The `dag_pkg` is a symlink that points to the repo root. I.e. `ln -s . dag_pkg`. This is needed to resemble the checkout used by MARS as mimicked by the entry points test. Someone more clever than I at python pathing and packaging may be able to get around it.

## TODO

- SQL and ETL explainers or links for those who are new to writing ETLs and/or nontrivial SQL.
- Python tooling for creating jobs and documentation
- The initial set of jobs
- Rename the `sql_jobs` dirs to `sql_tasks`
- Instructions for how to create MARS jobs
- Evergreen project
- Lockfile equivalents for requirements.txt file(s)
