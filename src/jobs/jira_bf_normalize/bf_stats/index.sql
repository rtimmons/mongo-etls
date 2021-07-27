with
    histories as (
        select
            id,
            issueid,
            created,
            cast(json_parse(items) 
                as array(row(field varchar, toString varchar,
                               "from" varchar, fromString varchar, 
                               "to" varchar, fieldtype varchar))) as deltas
        from    
            stagingawsdatacatalog.raw_jira.dw__jira__changelogs_full_history
    ),
    all_deltas as (
        select  hs.id as id,
                hs.issueid as issueid,
                hs.created as created,
                ds.field as "field",
                ds.tostring as "tostring",
                ds."from" as "from",
                ds."fromstring" as "fromstring",
                ds."to" as "to"
        from    histories hs,
                unnest(deltas) as ds
    ),
    first_changeds as (
        select  id,
                issueid,
                from_iso8601_timestamp(created) as created,
                field,
                tostring,
                "from",
                "fromstring",
                "to",
                -- TODO: use proper boolean types here
                if(created = (
                    -- is first time going from "from" to "to"
                    select  min(created)
                    from    all_deltas ms
                    where   ms.field = ds.field
                    and     (
                        (ms."from" is null and ds."from" is null)
                        or
                        (ms."from" is not null and 
                         ds."from" is not null and
                         ms."from" = ds."from")
                    )
                    and     (
                        (ms."to" is null and ds."to" is null)
                        or
                        (ms."to" is not null and 
                         ds."to" is not null and
                         ms."to" = ds."to")
                    )
                    and     ms.issueid = ds.issueid
                ), 'yes', 'no') as first_time_same_transition,
                if(created = (
                    -- is first time going from "from" to "to"
                    select  min(created)
                    from    all_deltas ms
                    where   ms.field = ds.field
                    and     ms."from" is null
                    and     ms."to" is not null
                    and     ms.issueid = ds.issueid
                ), 'yes', 'no') as first_time_not_null
        from    all_deltas ds
    ),
    aissues as (
        select  
                id                          as id,
                key                         as key,
                fields__status__name        as status,
                fields__priority            as priority,
                fields__resolution__name    as resolution,
                fields__assignee__name      as assignee,
                fields__customfield_14278   as evg_projects,
                if(fields__customfield_12950 like '%perf%',true,false) as on_perf_project,
                try(cast(fields__customfield_15550 as bigint))  as score,
            
                -- TODO: 'nan' values?
                fields__customfield_20463 as severity_types,

                (
                    /* TODO fix based on serde */
                    fields__customfield_20463 like '%Release Blocking%' and
                    fields__customfield_20463 not like '%Not Release Blocking%'
                ) as is_release_blocker,
        
                coalesce(
                    try(cast(fields__customfield_15550 as bigint)),
                    0
                ) > 100 as is_hot,
        
                fields__customfield_14277 like '%-required%' as on_required_buildvariant,
                fields__customfield_14277 like '%-suggested%'as on_suggested_buildvariant,
        
                (
                    fields__status__name = 'Closed' or
                    fields__status__name = 'Waiting for bug fix' or
                    fields__status__name = 'Resolved'
                ) as is_investigated,
        
                from_iso8601_timestamp(fields__created) as created_date,
        
                (
                    -- TODO: is this right?
                    -- showing as null for issueid=572968
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'project'
                    and   cs."fromstring" = 'Build Failure Genesis'
                    and   cs."tostring" = 'Build Failures'
                    and   cs.first_time_same_transition = 'yes'
                ) as converted_date, -- aka processed_date
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'assignee'
                    and   cs."tostring" is not null
                    and   cs.first_time_not_null = 'yes'
                ) as team_assigned_date,

                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'In Progress'
                    and   cs.first_time_not_null = 'yes'
                ) as began_investigation_date,

                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'Waiting for bug fix'
                    and   cs.first_time_same_transition = 'yes'
                ) as wfbf_date,
        
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'Stuck'
                    and   cs.first_time_same_transition = 'yes'
                ) as stuck_date,
        
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'priority'
                    and   cs."tostring" = 'Trivial - P5'
                    and   cs.first_time_same_transition = 'yes'
                ) as trivial_date,
                
        
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'Closed'
                    and   cs.first_time_same_transition = 'yes'
                ) as closed_date,

                -- nice to have maybe?
                fields__customfield_14277 as buildvariant, -- TODO: serde
                fields__customfield_16252 as failure_type,
                fields__customfield_12950 as evg_task,
                fields__customfield_16350 as count_of_linked_failures
        from
            stagingawsdatacatalog.raw_jira.dw__jira__issues issues
    )
select
    aissues.*,
    team_assigned_date - converted_date as time_buildbaron_triage,
    began_investigation_date - team_assigned_date as time_to_begin_investigation,
    wfbf_date - began_investigation_date as time_investigated,
    stuck_date - began_investigation_date as time_investigated_to_stuck,
    trivial_date - began_investigation_date as time_investigated_to_trivial,
    closed_date - wfbf_date as time_waiting_for_fix
from aissues
where 1=1
    and aissues.id in(
        '1451063',
        '1448714',
        '1448670',
        '1448661',
        '1448332',
        '1447295',
        '1446689',
        '1446124',
        '1445956',
        '1445819'
    );


