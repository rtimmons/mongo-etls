# R&D Dev-Prod ETLs

This repository contains all the ETLs that comprise the R&D Dev-Prod data pipeline. This pipeline runs on MARS and interacts with Presto and other data-sources.

```sh
git clone git@github.com:10gen/dev-prod-etls.git
cd dev-prod-etls
./ci.sh pytest
```

## Data Pipeline Components

When creating new jobs or components of the data-pipeline, please refer to the [Policies](./docs/policies.md) before sending PRs.

## TODO

- SQL and ETL explainers or links for those who are new to writing ETLs and/or nontrivial SQL.
- Python tooling for creating jobs and documentation
- The initial set of jobs
- Instructions for how to create MARS jobs
- Evergreen project
- Lockfile equivalents for requirements.txt file(s)
