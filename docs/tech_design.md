# Technical Design: Dev-Prod Data Platform

This is intended to be a set of guidelines and design decisions that all teams within dev-prod use as a starting point for any new or significantly changed work that is data-heavy.

Deviations are to be expected but must be well-reasoned and approved by a plurality of dev-prod technical leadership.

## TODO:

- Incorporate the DW guide https://docs.google.com/document/d/1_tBRWfUmRxx7E3nSCxQInc0jRFKk-mtV7NcqmEbZd5E/edit#heading=h.nmf3dg4tswn4

## Bureaucracy

This document is intentionally NOT a Google doc. This lives in the ETL repo for auditing and PR purposes.

**Changelog**:

- 2021-12-13: Initial version

## What Is the Future?

(This was written in 2021-12)

In 6 months:

- All dev-prod systems will have their most meaningful data accessible via Presto.
- We have a well-reasoned, well-structured, and well-supported data architecture that is robust in the face of operational issues, growing team and organizational complexity, and new engineer onboarding.
- Users both in and outside dev-prod can do ad-hoc and prepared queries against all dev-prod systems using Presto and MARS tooling.
- Charting and BI are enabled. (Although we may not have found all the right BI tools by this time.)
- A growing number of systems are using Presto to serve back-office requests such as test statistics.
- We know which APIs and systems would be obviated by further R&D with Presto and we have a timeline in place for making transitions (or explicit reasons to avoid doing so).
- Data analysis pipelines are done in whole or part using MARS jobs. E.g., TIPS jobs and rollup calculations are done as part of the TIPS MARS tooling.

In 2 years:

- We are using data across systems both within dev-prod and external to dev-prod to drive new investigations and new projects. For example: using Jira or org-chart data to inform test selection.
- All of our data pipelines are expressed in MARS jobs including log analysis, task-splitting, 
- Users are actively writing their own data-pipelines for the purposes of BF investigation, release underwriting, or management decision-making.
- No systems need to copy data from other systems. E.g. rather than calling Evergreen or Jira APIs in bulk, systems will be able to join with Evergreen and Jira data in Presto.
- The number of APIs we have is greatly reduced and instead focus solely on CRUD operations driven by user-intent.

Risks:

- We are not traditionally a BI organization. We have only nascent expertise in data-science. Identifying the right problems and solutions to solve with BI tooling will take some care and expertise.
- Maintaining backward-compatibility for data-based systems is similar but notably different from backward-compatibility for service-based systems.
- Similarly: organizing around data-pipelines is a different strategy from organizing around service-based systems. Ensuring that jobs are idempotent, dependencies are tracked, that fixes and backfills are possible but rarely needed, and that downstream data systems are sufficiently insulated are new skillsets for many of our engineers.

## Data-Flow

1. Dev-prod systems use Atlas as their primary data-store. Atlas is the store-of-record for all OLTP data. Each Atlas cluster has an Analytics Node exposed only to Presto, and each Atlas cluster is onboarded onto Presto as a new federation.
2. Teams may expose REST or other realtime APIs backed by Atlas. These APIs should be "OLTP"-style and should only interact with a *known* and *bounded* number of documents in Atlas. E.g. they should not do large aggregations, scanning of time- or usage-dependent/increasing datasets, or otherwise expensive queries that will ultimately affect the scalability of their systems.
3. Systems do not call services "in bulk" to get chunks of data. The request graph does not grow without bound.
4. OLAP data (aggregations, joins with other datasets, data-science, etc) all go through Presto.
5. Presto is used by MARS jobs to create query-friendly snapshots and views that can be joined with all other data in the Presto ecosystem.
6. Teams have "raw" (landing zone) schemas in Presto that represent snapshots of their entire Atlas data-sets. This "raw" data is volatile, and it changes as the schema and data within Atlas. Landing zone schemas are "private" to the team.
7. The "raw" data is exposed via "xforms" or "views". These are populated by MARS jobs written and owned by the team. E.g. `evergreen_landing` is transformed into `evergreen_view` via ETL jobs that the Evergreen team owns.
8. The "view" datasets are considered the "data APIs" and have explicit requirements on their schema, timeliness, and documentation as detailed by the "Policies" section below.

(I'm using "view" as a general term to represent the public dataset that teams maintain as their APIs. Under the covers, the object may be a table etc.)

## Changes from Status-Quo

1.  Teams will not be able to query Evergreen or other APIs "in bulk" to duplicate, materialize, or otherwise query Evergreen data. These queries will need to be run against the Presto views of the Evergreen/etc data.

2.  Users will not have access to Analytics Nodes. Rather, they will access teams' data using Presto.

3.  Users will not have access to raw data. They will instead have access to maintained views that have defined SLAs and guarantees of backward-compatibility.

4.  Data translations will be done in a well-defined ecosystem of MARS jobs and not one-off Kanopy or other Cron execution environments.

    See [Using an ETL framework vs writing yet another ETL script](https://airbyte.io/blog/etl-framework-vs-etl-script):

    > Your first ETL script will normally take the form of a CLI that calls an external API to extract some data, normalize it and load it to destination. You run it once and you think it's over...

## Policies

These policies are intended to be reasonable and balanced between the needs of customers to access their data and the needs of teams to iterate quickly.

In particular, this design and these policies are intended to make life easier on dev-prod teams by reducing surface-areas of APIs. Since exposing analytical data via APIs is discouraged, customers need consistent, reliable, and transparent access to data via views with the same expectations they would otherwise have on APIs.

These policies are not in order.

### All Data is Exposed (even if ugly)

Dev-prod does not produce data. We produce systems that let our customers produce, explore, and analyze their own data. We do not Smaug data in our systems. We do not become bottlenecks in letting our customers see their own data on our systems. As such, all data within our systems is exposed to the Presto ecosystem in the "raw" datasets.

**This does not mean every single data-point is available in Views**. Some data may be difficult to expose in views while features are work-in-progress. However: once raw data becomes stable as features reach maturity, data must be made available in views following the rest of these policies. 

**In general**: creating a supported view for new data is part of the success criteria for completing work on new data or new features.

### Raw data is Private and Unstable

If customers wish to access raw data that is not in views, they may do so but **at their own peril**. Some raw data is highly sensitive and must be kept team-internal. There is an explicit understanding that raw data is volatile in schema and without tight SLAs.

**Any processes that rely on raw data or connections to analytics nodes are subject to break without notice or recourse.**

### Views Data is Designed Intentionally

Put as much time and effort into designing your views as you would your application schema and your service's APIs. In essence, views are your APIs.

Care should be taken to not over- or under-normalize data. Views should take full advantage of Presto's abilities to traverse structured data-sets. This said, the ultimate consumer of view data is our customers and designing views for ease of use is an important consideration. Too many required joins makes life hard. No joins and mass-duplicated data makes life confusing.

We will accumulate a list of best-practices for what well-designed views include.

- each row in a view has
    - `updatedAt`
    - `insertedAt`
    - `xformedAt`
    - `deletedAt` (if relevant)
- For data related to evergreen, relevant rows should always include `version_id`, `task_id`, `build_variant`, and `execution`.

### Views Data is Public and Documented

**Public**:  
Each view is in the `dev_prod_live` schema.

**Documented**:  
Each view has an associated Alation record detailing the structure and usage, etc. The documentation must include the owning team as well as freshness SLAs.


### Views Data is Stable; Changes to Views Follow a Process

Any view living in `dev_prod_live` can be used by other teams to create business-critical processes that we must take great care to not break.

Changing the interpretation or type or cardinality of columns, deleting columns, etc. is bad. It can break systems may levels deep down the pipeline. This can take multiple days to become obvious, debugging can be very difficult, trust is lost, and data-fixes and backfills are expensive and risky. See "Changes to Views Follow a Process" for more information.

The following all represent breaking changes to a view:

- dropping columns
- renaming columns
- changing data types or structures
- changing the cardinality (e.g. merging two rows with array structures such that the view must now be unnested by queries)
- changing the business intent or meaning of columns. The same data is not represented differently today versus tomorrow.
- switching from hard deletes to soft deletes (tombstoning) or vice-versa
- large changes in SLAs (e.g. changing a view from hourly to daily or adding TTLs)

Note that adding columns is not a breaking change.

When a breaking change is needed, do the following:

1. Create a new view with a new name. Perhaps append a `v2` suffix.
2. Identify all stakeholders using the view and work with them to migrate to the new view.
3. Continue to support the current view for a minimum of 1 quarter or until all users of the view are both identified and ready to have the old view dropped.

In many cases this will be very simple. In others it may be impossible. Supporting multiple versions of a view in perpetuity is a risk, so designing views right the first time is a necessity. This is not dissimilar from designing an API right the first time.

### SLAs are Explicit

Each product producing data that is used within the dev-prod data ecosystem must document where its data lives and the timeliness of such data.

SLAs include:

- How timely the data is. If an event happens at time t0 how long will it take for that to show up in the view?
- How "far back" the dataset goes. If an event happens at t0, how long will the view include that data?

These SLAs are documented along with the view itself in Alation.

### Data is Never Too Stale

This is subjective. The below are guidelines and reasonable starting-point expectations. Each dataset will have to decide for itself and with its stakeholders how timely the data needs to be.

- Most analytical data can be 1 business-day delayed.
- Many complex reports can be generated daily or weekly.
- Realtime data cannot be delayed and is perhaps better suited to an API.
- Semi-realtime data (e.g. running statistics or approximations for dashboarding purposes) can be 1-3 hours delayed.
- Calculation processes that are part of a human-scale workload (e.g. patch-building) can be delayed by up to 30 minutes but not much longer.

Ask yourself what a reasonable consumer of this data would expect in terms of timeliness and balance that with the costs of keeping a tighter SLA.

Since SLAs are always explicit, they are included in design documents and/or product documentation. Stakeholders can see the SLA as a part of the design and push back when appropriate.

### Services are the APIs for OLTP

CRUD operations remain within kanopy/etc-deployed services that talk to Atlas.

### Presto is the API for OLAP

Services are for REST-style CRUD-esque interactions. Applications that need aggregations go through Presto, not bespoke service operations.

```
Today:
┌───┐   ┌────────┐   ┌─────────┐
│App├──▶│Service ├──▶│  Atlas  │
└───┘   └────────┘   └─────────┘

After:
┌───┐   ┌────────┐   ┌─────────┐
│App├──▶│ Presto ├──▶│  Atlas  │
└───┘   └────────┘   └─────────┘
```

### Applications Have Distinct Service Accounts

Each distinct deployment unit gets its own service account to use to connect to Presto.

### Analytics Nodes are Private

Query and operate against services (OLTP) or Presto (OLAP). The analytics nodes do not have a stable API and are not scaled to suit ad-hoc uses.

### Views Don't Query Atlas

No OLAP-style queries are done against Atlas-backed schemas.

Generally queries against data in Presto require multi-part operations. The underlying systems start by materializing or "snapshotting" the Atlas data "as-is" to a set of landing-zone tables. Large collections can be moved [incrementally](https://wiki.corp.mongodb.com/display/DW/Incremental+Load+Pattern). From there, translations are done on the snapshot data to produce the customer-facing views.

### When to Use APIs

Interact with APIs and not Presto whenever "writeback" is necessary: Workflow applications where UIs and other systems need to reflect real-time changes or information are not well-suited for Presto.

However: a well-designed system can use an API to track state with an API but underlying data in Presto. E.g. the presence of a change-point is in Presto but whether or not it's processed can be in an API. Care must be taken to not design frankenstein systems where there is no good source of truth.

### Views are Created Idempotently

The jobs to create views should be repeatably runnable. If there is a data-delay or other volatile error, the job must be able to either pick up where it left off or recreate its world from scratch.

### When Possible, Prefer "Presto" MARS tasks

[Presto tasks in MARS](https://mars-doc.dataplatform.prod.corp.mongodb.com/docs/Presto%20Task) let you define a SQL query along with a destination. While some logic is significantly easier or clearer in Python, the majority of our logic is easily expressible in SQL. Not knowing SQL is not a sufficient reason to go off these rails.

The recommended destination for Presto tasks is Presto tables. Occasionally jobs may wish to write the resultsets back to an Atlas cluster, but this should be carefully considered given the capabilities of Presto and the cost of large Atlas clusters for data that is largely append-only.

### Python Tasks Are Only for Translation

Only opt for [Python tasks](https://mars-doc.dataplatform.prod.corp.mongodb.com/docs/Python%20Task) when the task at hand is wildly unsuited for SQL. E.g., very complicated business-logic, logic living in other repositories, or calculations or operations that are impossible to express via SQL (e.g. numpy or unzipping files etc).

Not knowing SQL is not a sufficient reason to write a pipeline step in Python.

Do not use Python tasks for data ingestion. If data from outside sources is not available in Presto, schedule an onboarding with the Data Architecture team. There are many tools that they have to make ingesting new sources of data either no-code or low-code (e.g. [stitchdata](https://www.stitchdata.com/)).

(Again: this--along with the rest of this document--is merely a policy. Engineers are free to engineer differently at their own discretion and peril.)

### Views and Jobs Are Run by MARS

No Kanopy, ad-hoc Crons, or other systems are allowed to ingest data into the `dev_prod` namespace. All data going into the `dev_prod` namespace is orchestrated by MARS. This lets us easily search for usages and troubleshoot provenance issues.

### MARS Jobs Are Secure

All jobs must be defined in code, and all code must be code-reviewed.

MARS jobs are capable of leaking secrets since the service accounts that run them ultimately need the ability to access sensitive data. This is why we don't allow ad-hoc jobs to be created in the dev_prod namespace, and the service account that MARS uses is only available with the dev_prod namespace.

The `dev_prod` MARS namespace may only contain jobs that are defined using [dynamic config](https://mars-doc.dataplatform.prod.corp.mongodb.com/docs/Dynamic%20DAG), and that dynamic config must reference a repository that has strong code-review processes and auditability (e.g. protected branches). For now there is only one repo, `mongo-etls` that contains all jobs, although we can have additional jobs in the future.

To this end, only leads and above have permissions to create new jobs, and all jobs should follow the same template of being dynamic-configs.

(Note: This is a hard requirement. There will be no exceptions to this. We take the security of our data and systems seriously.)

### Naming Policies

This is still WIP and needs some more examples to feel confident in what scales to complexity.

- Jobs are named by their business purpose
- Raw (source) tables are named by `${project}_${entity}`
- View (results) tables are named following `${project}_${entity}_v${version}`
    - `project` is arbitrary but gives a namespace for entities. Example projects would be "evergreen", "bf_manager", "results", etc.
    - `entity` is the **plural** version of the nouns that live in the table. Examples would be "project_versions", "correctness_results", "bfs", etc.
    - `version` starts at 1 and is incremented whenever there is a breaking change. See the breaking changes policy for more info
    - Example: `results_correctness_results_v1`


## Design Alternatives: Airflow

Airflow is a more sophisticated and thus complicated replacement for MARS. MARS is an in-house tool whereas Airflow is a growing industry-standard for similar kinds of data-pipeline orchestration.

We believe that our pipelines will be simple enough to fall within MARS's capabilities for the foreseeable future. Airflow is yet another tool with limited expertise in our organization.

MARS

- Abstractions built for common data tasks such as exporting to GSheet, S3 or materializing as tables.
- More of UI/configuration focused
- Simple pipelines can be defined in code
- No infrastructure / service to be managed by users

Airflow

- Flexibility via code. (Anything you can code in Python, you can run as a part of your pipeline refresh cycle)
- Customization of the infra/system and integration is needed
- Direct infrastructure & access to scheduler needed
- More "native" CI/CD integration: Since airflow pipelines are defined as code, it's possible to deploy pipelines via drone pipeline.
- Sophisticated tooling without expertise within dev-prod.

Airflow is pretty powerful. To the extent where many services actually build right on top of it. But it also means that it comes with some overhead to get started and maintain.

If we outgrow MARS, the above design and policies are designed to allow an eventual transition to Airflow without significant pain. Since we use Kanopy, we can use existing kanopy charts to spin up and manage our own isntance. The logic and structure of all jobs live as code. Any such transition to Airflow would involve re-wiring the current logic, likely not having to re-implement anything significantly.

