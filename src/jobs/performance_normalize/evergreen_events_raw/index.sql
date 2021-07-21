--
-- populate awsdatacatalog.dev_prod_metrics_v1.evergreen_events_raw
--

WITH src as (
    select
        cast(_id as varchar) as "_id",
        eventtype,
        versionid,
        patch,
        alias,
        branch,
        author,
        team,
        "project",
        versionstranded,
        versiontotaltimetakeninsec,
        versiontasksuccesscount,
        versiontaskfailurecount,
        versiontasksystemfailurecount,
        versiontasktimedoutcount,
        versionpcttasksuccess,
        versionpcttaskfailure,
        versionpcttaskssystemfailure,
        versionpcttasktimedout,
        versionestimatedcost,
        date(calculatedat) as "calculatedat",
        buildmakespantostartinsec,
        buildmakespantofinishinsec,
        buildvariant,
        taskname,
        taskmakespantostartinsec,
        taskmakespantofinishinsec
    from
        evergreen_metrics_atlas.versions.events as src
)
SELECT
    *
FROM    
    src
    left outer join     -- we have all of src
    awsdatacatalog.dev_prod_metrics_v1.evergreen_events_raw as dest
    on src._id = dest._id
where
    dest._id is null -- but where the join was outer (no match)
