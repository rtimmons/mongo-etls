-- attempts to mimic 
--   https://github.com/10gen/pm-resources/blob/411dcbbb4e02ab12c7a9f0af94e9427a53f80ae8/python_scripts/load_bf_data.py#L45
-- in sql
with
    histories_t as (
        select
            id,
            issueid,
            created,
            -- TODO: any better to put this in the lower `histories` view?
            cast(json_parse(items) 
                as array(row(field varchar, toString varchar,
                               "from" varchar, fromString varchar, 
                               "to" varchar, fieldtype varchar))) as deltas,
            rank() over (partition by id order by "_history_date" desc, _sdc_sequence desc) as rnk
        from
            stagingawsdatacatalog.raw_jira.dw__jira__changelogs_full_history
    ),
    histories as (
        select id, issueid, created, deltas
        from histories_t
        where rnk = 1
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
        select  distinct -- some jira bugs e.g. 143693
                issueid,
                from_iso8601_timestamp(created) as created,
                field,
                "fromstring",
                "tostring",
                if(created = (
                    -- is first time going from "fromstring" to "tostring"
                    select  min(created)
                    from    all_deltas ms
                    where   ms.field = ds.field
                    and     (
                        (ms."fromstring" is null and ds."fromstring" is null)
                        or
                        (ms."fromstring" is not null and 
                         ds."fromstring" is not null and
                         ms."fromstring" = ds."fromstring")
                    )
                    and     (
                        (ms."tostring" is null and ds."tostring" is null)
                        or
                        (ms."tostring" is not null and 
                         ds."tostring" is not null and
                         ms."tostring" = ds."tostring")
                    )
                    and     ms.issueid = ds.issueid
                ), 'yes', 'no') as first_time_same_transition,

                if(created = (
                    -- is last time going from "from" to "to"
                    select  max(created)
                    from    all_deltas ms
                    where   ms.field = ds.field
                    and     (
                        (ms."fromstring" is null and ds."fromstring" is null)
                        or
                        (ms."fromstring" is not null and 
                         ds."fromstring" is not null and
                         ms."fromstring" = ds."fromstring")
                    )
                    and     (
                        (ms."tostring" is null and ds."tostring" is null)
                        or
                        (ms."tostring" is not null and 
                         ds."tostring" is not null and
                         ms."tostring" = ds."tostring")
                    )
                    and     ms.issueid = ds.issueid
                ), 'yes', 'no') as last_time_same_transition,
                if(created = (
                    -- is first time going from "from" to "to"
                    select  min(created)
                    from    all_deltas ms
                    where   ms.field = ds.field
                    and     ms."fromstring" is null
                    and     ms."tostring" is not null
                    and     ms.issueid = ds.issueid
                    and     ds."fromstring" is null
                    and     ms."tostring" is not null
                ), 'yes', 'no') as first_time_not_null,
                if(created = (
                    select max(created)
                    from all_deltas ms
                    where ms.field = ds.field
                    and   ms.issueid = ds.issueid
                    and   ms."tostring" = ds."tostring"
                ), 'yes', 'no') as last_time_to_value,
                if(created = (
                    select min(created)
                    from all_deltas ms
                    where ms.field = ds.field
                    and   ms.issueid = ds.issueid
                    and   ms."tostring" = ds."tostring"
                ), 'yes', 'no') as first_time_to_value
        from    all_deltas ds
    ),
    aissues_t as (
        select  
                id                          as id,
                key                         as key,
                fields__status__name        as status,
                -- fields__priority            as priority,
                fields__resolution__name    as resolution,
                fields__assignee__name      as assignee,
                fields__customfield_14278   as evg_projects,
                -- if(fields__customfield_12950 like '%perf%',true,false) as on_perf_project,
                coalesce(
                    try(cast(fields__customfield_15550 as bigint)),
                    0
                ) as score,
            
                /*
                if(fields__customfield_20463='nan', null, fields__customfield_20463) as severity_types,
                */

                /*
                (
                    -- TODO fix based on serde
                    fields__customfield_20463 like '%Release Blocking%' and
                    fields__customfield_20463 not like '%Not Release Blocking%'
                ) as is_release_blocker,
                */

                /*
                coalesce(
                    try(cast(fields__customfield_15550 as bigint)),
                    0
                ) > 100 as is_hot,
                */
        
                /*
                fields__customfield_14277 like '%-required%' as on_required_buildvariant,
                fields__customfield_14277 like '%-suggested%'as on_suggested_buildvariant,
                */
        
                /*
                (
                    fields__status__name = 'Closed' or
                    fields__status__name = 'Waiting for bug fix' or
                    fields__status__name = 'Resolved'
                ) as is_investigated,
                */
        
                /*
                from_iso8601_timestamp(fields__created) as created_date,
                */
        
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
                ) as first_team_assigned_date,
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'In Progress'
                    and   cs.first_time_to_value = 'yes'
                ) as began_investigation_date,

                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'Waiting for bug fix'
                    and   cs.first_time_to_value = 'yes'
                ) as wfbf_date,
        
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'Stuck'
                    and   cs.first_time_to_value = 'yes'
                ) as stuck_date,
        
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'priority'
                    and   cs."tostring" = 'Trivial - P5'
                    and   cs.first_time_to_value = 'yes'
                ) as trivial_date,
                
        
                (
                    select created
                    from  first_changeds cs
                    where cs.issueid = issues.id
                    and   cs.field = 'status'
                    and   cs."tostring" = 'Closed'
                    and   cs.first_time_to_value = 'yes'
                ) as closed_date,

                rank() over(partition by id order by _sdc_sequence desc) as rnk

                -- nice to have maybe?
                /*
                fields__customfield_14277 as buildvariant, -- TODO: serde
                fields__customfield_16252 as failure_type,
                fields__customfield_12950 as evg_task,
                fields__customfield_16350 as count_of_linked_failures
                */
        from
            stagingawsdatacatalog.raw_jira.dw__jira__issues issues
    ),
    aissues as (
        select *
        from aissues_t
        where rnk = 1
    )
select
    aissues.*,
    to_milliseconds(first_team_assigned_date - converted_date) / 3600000 as time_buildbaron_triage,
    to_milliseconds(began_investigation_date - first_team_assigned_date) / 3600000 as time_to_begin_investigation,
    to_milliseconds(wfbf_date - began_investigation_date) / 3600000 as time_investigated,
    to_milliseconds(stuck_date - began_investigation_date) / 3600000 as time_investigated_to_stuck,
    to_milliseconds(trivial_date - began_investigation_date) / 3600000 as time_investigated_to_trivial,
    to_milliseconds(closed_date - wfbf_date) / 3600000 as time_waiting_for_fix
from aissues
where aissues.key like 'BF%'

