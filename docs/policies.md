# Policies
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


## TODO:

- Incorporate the DW guide https://docs.google.com/document/d/1_tBRWfUmRxx7E3nSCxQInc0jRFKk-mtV7NcqmEbZd5E/edit#heading=h.nmf3dg4tswn4


