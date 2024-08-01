drop function if exists subtract_period_from_date;
CREATE OR REPLACE FUNCTION subtract_period_from_date(input_date DATE, period_interval INTERVAL)
RETURNS DATE AS
$$
BEGIN
    RETURN input_date - period_interval;
END;
$$
LANGUAGE plpgsql;

drop function if exists get_business_hour_day_for_grafana;
CREATE OR REPLACE FUNCTION get_business_hour_day_for_grafana(duration_in_minute FLOAT, business_day_minutes FLOAT)
RETURNS FLOAT AS $$
DECLARE
    calculated_duration FLOAT;
BEGIN
    IF duration_in_minute < business_day_minutes THEN
        calculated_duration := duration_in_minute;
    ELSE
        calculated_duration := (duration_in_minute / business_day_minutes) * 24.0 * 60.0;
    END IF;
    
    RETURN calculated_duration;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ISEMPTY(value TEXT)
RETURNS BOOLEAN
AS $$
BEGIN
    RETURN value IS NULL OR value = '' OR length(trim(value)) = 0;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS get_week_day;
CREATE OR REPLACE FUNCTION get_week_day(input_date ANYELEMENT)
RETURNS TABLE (date DATE, day_of_week NUMERIC, day_of_week_str TEXT, is_weekend BOOLEAN) AS $$
BEGIN
    RETURN QUERY (
        SELECT 
            input_date::DATE,
            EXTRACT(ISODOW FROM input_date::DATE) AS day_of_week,
            ((EXTRACT(dow FROM input_date::DATE) + 6) % 7 + 1)::TEXT || '-' || TO_CHAR(input_date::DATE, 'Dy')  AS day_of_week_str,
            EXTRACT(ISODOW FROM input_date::DATE) IN (6, 7) AS is_weekend
    );
END;
$$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS get_dates_table;
CREATE OR REPLACE FUNCTION get_dates_table(start_date TEXT, end_date TEXT)
RETURNS TABLE (date DATE, day_of_week NUMERIC, day_of_week_str TEXT, is_weekend BOOLEAN) AS $$
BEGIN
    RETURN QUERY (
        SELECT
            dates.day_date as date,
            (EXTRACT(dow FROM dates.day_date) + 6) % 7 + 1 as day_of_week,
            ((EXTRACT(dow FROM dates.day_date) + 6) % 7 + 1)::TEXT || '-' || TO_CHAR(dates.day_date, 'Dy') AS day_of_week_str,
            CASE WHEN EXTRACT(dow FROM dates.day_date) IN (0, 6) THEN TRUE ELSE FALSE end as is_weekend
        FROM
        (
            SELECT generate_series(start_date::TIMESTAMP, end_date::TIMESTAMP, '1 day'::interval)::date AS day_date
        ) dates
    );
END;
$$ LANGUAGE plpgsql;

DROP materialized VIEW IF EXISTS dates;
create materialized view dates as 
select * from public.get_dates_table('2000-01-01', '2030-01-01');
CREATE INDEX idx_date ON dates(date);



DROP FUNCTION IF EXISTS get_dates;
CREATE OR REPLACE FUNCTION get_dates(start_date TEXT default '2000-01-01', end_date TEXT default '2030-01-01')
RETURNS TABLE (date DATE, day_of_week NUMERIC, day_of_week_str TEXT, is_weekend BOOLEAN) AS $$
BEGIN
    RETURN QUERY (
        SELECT * 
        FROM public.dates d
        WHERE d.date BETWEEN start_date::TIMESTAMP AND end_date::TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_timeranges(start_time text, end_time text, timerange_in_minutes INTEGER)
RETURNS TABLE(time_range text)
LANGUAGE plpgsql
AS $function$
DECLARE
    start_hour INT;
    start_minute INT;
    end_hour INT;
    end_minute INT;
    current_hour INT;
    current_minute INT;
BEGIN
    start_hour := CAST(SUBSTRING(start_time, 1, 2) AS INT);
    start_minute := CAST(SUBSTRING(start_time, 4, 2) AS INT);
    
    end_hour := CAST(SUBSTRING(end_time, 1, 2) AS INT);
    end_minute := CAST(SUBSTRING(end_time, 4, 2) AS INT);
    
    current_hour := start_hour;
    current_minute := start_minute;
    
    WHILE (current_hour < end_hour) OR (current_hour = end_hour AND current_minute <= end_minute) LOOP
        time_range := TO_CHAR(current_hour, 'FM00') || ':' || TO_CHAR(current_minute, 'FM00') || '-' ||
                      TO_CHAR((current_hour + (current_minute + timerange_in_minutes) / 60) % 24, 'FM00') || ':' ||
                      TO_CHAR((current_minute + timerange_in_minutes) % 60, 'FM00');
        
        IF (current_hour + (current_minute + timerange_in_minutes) / 60) % 24 < end_hour OR
           ((current_hour + (current_minute + timerange_in_minutes) / 60) % 24 = end_hour AND (current_minute + timerange_in_minutes) % 60 <= end_minute) THEN
            RETURN NEXT;
        END IF;
        
        current_hour := (current_hour + (current_minute + timerange_in_minutes) / 60) % 24;
        current_minute := (current_minute + timerange_in_minutes) % 60;
    END LOOP;
END;
$function$
;



drop function if exists is_time_in_timerange;
CREATE OR REPLACE FUNCTION is_time_in_timerange(
    given_time TEXT,
    timerange TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    given_hour INT;
    given_minute INT;
    start_hour INT;
    start_minute INT;
    end_hour INT;
    end_minute INT;
    given_time_in_minutes INT;
    timerange_start_in_minutes INT;
    timerange_end_in_minutes INT;
BEGIN
    -- Extraire l'heure et les minutes de l'heure donnée
    given_hour := CAST(SUBSTRING(given_time, 1, 2) AS INT);
    given_minute := CAST(SUBSTRING(given_time, 4, 2) AS INT);
    
    -- Extraire l'heure de début et de fin de la plage horaire
    start_hour := CAST(SUBSTRING(timerange, 1, 2) AS INT);
    start_minute := CAST(SUBSTRING(timerange, 4, 2) AS INT);
    end_hour := CAST(SUBSTRING(timerange, 7, 2) AS INT);
    end_minute := CAST(SUBSTRING(timerange, 10, 2) AS INT);
    
    -- Convertir l'heure donnée et l'heure de début de la plage horaire en minutes depuis minuit
    given_time_in_minutes := given_hour * 60 + given_minute;
    timerange_start_in_minutes := start_hour * 60 + start_minute;
    timerange_end_in_minutes := end_hour * 60 + end_minute;
    
    -- Vérifier si l'heure donnée est comprise dans la plage horaire
    IF timerange_start_in_minutes <= given_time_in_minutes AND given_time_in_minutes < timerange_end_in_minutes THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION convert_to_range(input_value INT, min_value INT, range_size INT)
RETURNS TEXT AS $$
DECLARE
    range_min INT;
    range_max INT;
BEGIN
    range_min := min_value + (FLOOR((input_value - min_value) / range_size) * range_size);
    range_max := range_min + range_size;
    
    RETURN '[' || range_min || ', ' || range_max || ']';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION to_timezone(
    date_utc timestamptz,
    timezone_dest text
)
RETURNS timestamp without time zone
AS $$
BEGIN
    RETURN date_utc AT TIME ZONE timezone_dest;
END;
$$ LANGUAGE plpgsql;



DROP FUNCTION IF EXISTS filter_pull_requests;
CREATE OR REPLACE FUNCTION filter_pull_requests(
    created_by TEXT DEFAULT NULL, 
    approved_by TEXT DEFAULT NULL, 
    target_branch_value TEXT DEFAULT NULL,
    feature_type TEXT DEFAULT NULL,
    start_date TEXT DEFAULT NULL, 
    end_date TEXT DEFAULT NULL, 
    repositories TEXT DEFAULT NULL,
    merge_time_interval TEXT DEFAULT '360d',
    timezone text default 'Europe/Paris'
)
RETURNS TABLE (
    pr_id VARCHAR,
    type VARCHAR,
    title VARCHAR,
    creation_day DATE,
    completion_day DATE,
    approvers_names TEXT,
    completion_date TIMESTAMP,
    creation_date TIMESTAMP,
    created_by_name VARCHAR,
    merge_time FLOAT,
    first_comment_delay FLOAT,
    count_inserted_lines BIGINT,
    count_deleted_lines BIGINT,
    creation_week_day TEXT,
    completion_week_day TEXT
) 
AS $$
DECLARE
    merge_time_interval_value FLOAT; -- Déclaration de la variable intervalle
    interval_value FLOAT; -- Valeur de l'intervalle (1, 2, etc.)
    interval_unit CHAR(1); -- Unité de l'intervalle (h, d, etc.)
BEGIN
    -- Extraction de la valeur et de l'unité de l'intervalle
    interval_value := CAST(LEFT(merge_time_interval, LENGTH(merge_time_interval) - 1) AS FLOAT);
    interval_unit := RIGHT(merge_time_interval, 1);

    -- Conversion de l'unité en intervalle PostgreSQL
    CASE 
        WHEN interval_unit = 'h' THEN
            merge_time_interval_value := (interval_value * 60);
        WHEN interval_unit = 'd' THEN
            merge_time_interval_value := (interval_value * 24 * 60);
        ELSE
            RAISE EXCEPTION 'Invalid merge_time_interval format';
    END CASE;
    
    RETURN QUERY 
    SELECT
        rows.*,
        creation_dates.day_of_week_str as creation_week_day,
        completion_dates.day_of_week_str completion_week_day
    FROM (
        SELECT DISTINCT
            pr.id AS pr_id,
            pr.type AS type,
            pr.title,
            CAST(DATE_TRUNC('day', public.to_timezone(pr.creation_date, timezone)) AS DATE) AS creation_day,
            CAST(DATE_TRUNC('day', public.to_timezone(pr.completion_date, timezone)) AS DATE) AS completion_day,
            STRING_AGG(DISTINCT vd.name, ',') AS approvers_names,
            public.to_timezone(pr.completion_date, timezone) as completion_date,
            public.to_timezone(pr.creation_date, timezone) as creation_date,
            created_by_developer.name as created_by_name,
            pr.merge_time,
            pr.first_comment_delay,
            ft.count_inserted_lines::BIGINT as count_inserted_lines,
            ft.count_deleted_lines::BIGINT as count_deleted_lines
        FROM public.pull_requests pr
        LEFT JOIN public.developers created_by_developer ON created_by_developer.id = pr.created_by_id
        LEFT JOIN public.pull_request_approvers pr_approvers on pr_approvers.pull_request_id = pr.id
        LEFT JOIN public.developers vd ON vd.id = pr_approvers.approver_id
        LEFT JOIN public.features ft ON ft.commit = pr.commit
        WHERE 
            -- filter: period
            1 = 1 
            AND (public.ISEMPTY(created_by) or created_by_developer.name = ANY(string_to_array(created_by, ',')) )
            and ((public.ISEMPTY(start_date) or public.ISEMPTY(end_date)) OR pr.creation_date BETWEEN start_date::TIMESTAMP AND end_date::TIMESTAMP)
            -- filter: approved_by
            AND (
                (public.ISEMPTY(approved_by) or vd.name is NULL or vd.name = ANY(string_to_array(approved_by, ',')))
            )
            -- filter: merge_time_interval
            AND (pr.merge_time)::FLOAT <= merge_time_interval_value
            -- filter: branch
            and (public.ISEMPTY(target_branch_value) or (pr.target_branch)::TEXT = ANY(string_to_array(target_branch_value, ',')))
            -- filter: type
            and (public.ISEMPTY(feature_type) or (pr.type)::TEXT = ANY(string_to_array(feature_type, ',')))
            -- filter: repository
            and (public.ISEMPTY(repositories) or (pr.repository)::TEXT = ANY(string_to_array(repositories, ',')))
            
        GROUP by
            pr.id,
            pr.type,
            pr.title,
            pr.creation_date,
            pr.completion_date,
            created_by_developer.name,
            pr.merge_time,
            pr.first_comment_delay,
            ft.count_inserted_lines,
            ft.count_deleted_lines
        ) rows
        LEFT JOIN public.get_dates() creation_dates ON rows.creation_day = creation_dates.date
        LEFT JOIN public.get_dates() completion_dates ON rows.completion_day = completion_dates.date
        ;
END;
$$ LANGUAGE plpgsql;





DROP FUNCTION IF EXISTS filter_comments;
CREATE OR REPLACE FUNCTION filter_comments(
    commented_by text default NULL, 
    created_by text default NULL, 
    approved_by text default NULL, 
    target_branch_value text default NULL,
    feature_type text default NULL,
    start_date text default NULL, 
    end_date text default NULL, 
    repositories text default NULL,
    merge_time_interval TEXT DEFAULT '360d',
    timezone text default 'Europe/Paris'
)
RETURNS TABLE (
    comment_id VARCHAR,
    pr_id VARCHAR,
    comment_date TIMESTAMP,
    commenter_name VARCHAR, 
    comment_length INTEGER,
    comment_content VARCHAR,
    created_by_name VARCHAR
)
AS $$
BEGIN
    RETURN QUERY 
    SELECT
    	c.id AS comment_id,
        pr.pr_id,
        public.to_timezone(c.creation_date, timezone) as comment_date,
        commenter.name as commenter_name,
        LENGTH(c.content) AS comment_length,
        c.content AS comment_content,
        pr.created_by_name
    FROM public.comments c
    INNER JOIN public.filter_pull_requests(
    	created_by,
    	approved_by,
    	target_branch_value,
    	feature_type,
    	start_date,
    	end_date,
    	repositories,
    	merge_time_interval,
    	timezone
    ) pr ON c.pull_request_id = pr.pr_id
    LEFT JOIN public.developers commenter on commenter.id = c.developer_id
    LEFT JOIN public.pull_request_approvers pr_approvers on pr_approvers.pull_request_id = pr.pr_id
    LEFT JOIN public.developers vd ON vd.id = pr_approvers.approver_id
    WHERE 
        1 = 1 
        -- filter: commented_by
        AND c.pull_request_id = pr.pr_id and pr.created_by_name != commenter.name
        AND (public.ISEMPTY(commented_by) or commented_by = '-' or (commenter.name)::TEXT = ANY(string_to_array(commented_by, ',')))
    group by 
        c.id,
        pr.pr_id,
        c.content,
        c.creation_date,
        commenter.name,
        c.content,
        pr.created_by_name;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS get_comments_or_pull_requests;
CREATE OR REPLACE FUNCTION get_comments_or_pull_requests(
    commented_by text default NULL, 
    created_by text default NULL, 
    approved_by text default NULL, 
    target_branch_value text default NULL,
    feature_type text default NULL,
    start_date text default NULL, 
    end_date text default NULL, 
    repositories text default NULL,
    merge_time_interval TEXT DEFAULT '360d',
    timezone text default 'Europe/Paris'
)
RETURNS TABLE (
    comment_id VARCHAR,
    comment_date TIMESTAMP,
    commenter_name VARCHAR, 
    comment_length INTEGER,
    comment_content VARCHAR,
    pr_id VARCHAR,
    type VARCHAR,
    title VARCHAR,
    creation_week_day TEXT,
    creation_day DATE,
    completion_week_day TEXT,
    completion_day DATE,
    approvers_names TEXT,
    completion_date TIMESTAMP,
    creation_date TIMESTAMP,
    created_by_name VARCHAR,
    merge_time FLOAT,
    first_comment_delay FLOAT,
    count_inserted_lines BIGINT,
    count_deleted_lines BIGINT
)
AS $$
BEGIN
    RETURN QUERY 
    SELECT comments.comment_id,
        comments.comment_date,
        comments.commenter_name, 
        comments.comment_length,
        comments.comment_content,
        pr.pr_id,
        pr.type,
        pr.title,
        pr.creation_week_day,
        pr.creation_day,
        pr.completion_week_day,
        pr.completion_day,
        pr.approvers_names,
        pr.completion_date,
        pr.creation_date,
        pr.created_by_name,
        pr.merge_time,
        pr.first_comment_delay,
        pr.count_inserted_lines,
        pr.count_deleted_lines
    FROM public.filter_pull_requests(
        created_by,
        approved_by,
        target_branch_value,
        feature_type,
        start_date,
        end_date,
        repositories,
        merge_time_interval,
        timezone
    ) pr
    LEFT JOIN public.filter_comments(
        commented_by,
        NULL, 
        NULL, 
        NULL, 
        NULL, 
        NULL, 
        NULL, 
        NULL, 
        merge_time_interval,
        timezone
    ) comments ON comments.pr_id = pr.pr_id 
    WHERE NOT public.ISEMPTY(pr.approvers_names) AND
    (
        CASE 
            WHEN commented_by = '-' THEN comments.comment_id is null
            WHEN NOT public.ISEMPTY(commented_by) THEN comments.comment_id is not null
            ELSE TRUE
        END
    );
END;
$$ LANGUAGE plpgsql;




-- Indicators for grafana
DROP FUNCTION IF EXISTS get_summary_statistics;
CREATE OR REPLACE FUNCTION get_summary_statistics(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
    nb_pull_requests bigint,
    nb_comments_by_pr double precision,
    comments_length_by_pr bigint,
    merge_time double precision,
    first_comment_delay double precision,
    count_changed_lines double precision,
    count_delta_changed_lines double precision
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        count(distinct p.pr_id) as nb_pull_requests,
        (count(distinct comment_id)::FLOAT) / nullif(count(distinct p.pr_id), 0) AS nb_comments_by_pr,
        sum(COALESCE(comment_length,0)) / nullif(count(distinct p.pr_id), 0) AS comments_length_by_pr,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.merge_time) as merge_time,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.first_comment_delay) as first_comment_delay,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.count_inserted_lines + p.count_deleted_lines) as count_changed_lines,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.count_inserted_lines - p.count_deleted_lines) as count_delta_changed_lines
    FROM public.get_comments_or_pull_requests(
        commented_by_param,
        created_by_param,
        reviewed_by_param,
        target_branch_param,
        type_param,
        from_date_param,
        to_date_param,
        repository_param
    ) as p;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS get_summary_statistics_by_week_day;
CREATE OR REPLACE FUNCTION get_summary_statistics_by_week_day(
    date_ref text,
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
    week_day text,
    nb_pull_requests bigint,
    nb_comments_by_pr double precision,
    comments_length_by_pr bigint,
    merge_time double precision,
    first_comment_delay double precision,
    count_changed_lines double precision,
    count_delta_changed_lines double precision
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE
            WHEN 'completion' = date_ref THEN p.completion_week_day
            ELSE p.creation_week_day
        END as week_day, 
        count(distinct p.pr_id) as nb_pull_requests,
        (count(distinct comment_id)::FLOAT) / nullif(count(distinct p.pr_id), 0) AS nb_comments_by_pr,
        sum(COALESCE(comment_length,0)) / nullif(count(distinct p.pr_id), 0) AS comments_length_by_pr,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.merge_time) as merge_time,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.first_comment_delay) as first_comment_delay,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.count_inserted_lines + p.count_deleted_lines) as count_changed_lines,
        PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY p.count_inserted_lines - p.count_deleted_lines) as count_delta_changed_lines
    FROM public.get_comments_or_pull_requests(
        commented_by_param,
        created_by_param,
        reviewed_by_param,
        target_branch_param,
        type_param,
        from_date_param,
        to_date_param,
        repository_param
    ) as p
    GROUP BY week_day
    ORDER BY week_day ASC;
END;
$$ LANGUAGE plpgsql;










DROP FUNCTION IF EXISTS get_number_of_comments_by_pull_requests;
CREATE OR REPLACE FUNCTION get_number_of_comments_by_pull_requests(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
    nb bigint,
    min_count_comments bigint,
    range text
) AS $$
BEGIN
    RETURN QUERY
    select 
    count(*) as nb, 
    min(count_comments) as min_count_comments,
    CASE 
        WHEN count_comments = 0 THEN 'No comment'
        WHEN count_comments = 1 THEN '1 comment' 
        WHEN count_comments = 2 AND count_comments <= 2 THEN '2 comments' 
        WHEN count_comments >= 3 AND count_comments <= 5 THEN '[3-5] comments' 
        ELSE '> 5' 
    END
    as range
    from (
        SELECT 
        p.pr_id,
        COUNT(distinct p.comment_id) as count_comments
        FROM public.get_comments_or_pull_requests(
            commented_by_param,
            created_by_param,
            reviewed_by_param,
            target_branch_param,
            type_param,
            from_date_param,
            to_date_param,
            repository_param
        ) p
        group by p.pr_id
    ) v
    group by range
    order by min_count_comments;
END;
$$ LANGUAGE plpgsql;






DROP FUNCTION IF EXISTS get_comments_stats_by_commenters;
CREATE OR REPLACE FUNCTION get_comments_stats_by_commenters(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
	name text,
    nb_pr bigint,
    nb_comments bigint,
    comment_length_sum bigint,
    comment_length_avg double precision,
    total_nb_pr bigint,
	total_nb_comments bigint,
	total_comment_length_sum bigint,
	total_comment_length_avg double precision,
	nb_pr_not_commented bigint
) AS $$
BEGIN
    RETURN QUERY
    select 
        by_commenter.*,
        total.*,
        total.total_nb_pr - by_commenter.nb_pr as nb_pr_not_commented
        from (
            SELECT
            p.commenter_name::text as name,
            COUNT(DISTINCT p.pr_id)::bigint as nb_pr,
            SUM(CASE WHEN p.commenter_name IS NOT NULL THEN 1.0 ELSE 0.0 END)::bigint as nb_comments,
            SUM(p.comment_length)::bigint as comment_length_sum,
            SUM(p.comment_length) / nullif(SUM(CASE WHEN p.commenter_name IS NOT NULL THEN 1.0 ELSE 0.0 END), 0)::FLOAT as comment_length_avg
            FROM public.get_comments_or_pull_requests(
                commented_by_param,
                created_by_param,
                reviewed_by_param,
                target_branch_param,
                type_param,
                from_date_param,
                to_date_param,
                repository_param
            ) p
            WHERE p.comment_id is not NULL
            GROUP BY p.commenter_name
        ) by_commenter
        CROSS JOIN (
            SELECT
            COUNT(DISTINCT p.pr_id)::bigint as total_nb_pr,
            SUM(CASE WHEN p.commenter_name IS NOT NULL THEN 1.0 ELSE 0.0 END)::bigint as total_nb_comments,
            SUM(p.comment_length)::bigint as total_comment_length_sum,
            SUM(p.comment_length) / nullif(SUM(CASE WHEN p.commenter_name IS NOT NULL THEN 1.0 ELSE 0.0 END), 0)::FLOAT as total_comment_length_avg
            FROM public.filter_comments(
                commented_by_param,
                created_by_param,
                reviewed_by_param,
                target_branch_param,
                type_param,
                from_date_param,
                to_date_param,
                repository_param
            ) p
        ) total;
END;
$$ LANGUAGE plpgsql;








DROP FUNCTION IF EXISTS get_comments_stats_by_approvers;
CREATE OR REPLACE FUNCTION get_comments_stats_by_approvers(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
	approver_name text,
    nb_pull_requests bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        approvers.name::TEXT as approver_name,
        COUNT(DISTINCT pr_id)::bigint as nb_pull_requests
        FROM public.get_comments_or_pull_requests(
            commented_by_param,
            created_by_param,
            reviewed_by_param,
            target_branch_param,
            type_param,
            from_date_param,
            to_date_param,
            repository_param
        )
        LEFT JOIN LATERAL unnest(string_to_array(approvers_names, ',')) AS approvers(name) ON true
        group by 
        approvers.name;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS get_sankey_reviewers;
CREATE OR REPLACE FUNCTION get_sankey_reviewers(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
	commenter_name text,
	created_by_name text,
    number_comments bigint,
    number_pr bigint
) AS $$
BEGIN
    RETURN QUERY 
    SELECT 
		p.commenter_name::text as commenter_name,
		p.created_by_name::text as created_by_name,
		count(distinct p.comment_id)::bigint as number_comments,
		count(distinct p.pr_id)::bigint as number_pr
		FROM public.get_comments_or_pull_requests(
            commented_by_param,
            created_by_param,
            reviewed_by_param,
            target_branch_param,
            type_param,
            from_date_param,
            to_date_param,
            repository_param
		) p
		where p.commenter_name is not null
		group by 
		p.commenter_name,
		p.created_by_name;
END;
$$ LANGUAGE plpgsql;




DROP FUNCTION IF EXISTS get_review_by_time_ranges;
CREATE OR REPLACE FUNCTION get_review_by_time_ranges(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
	week_day text,
	time_range text,
    count_comments bigint
) AS $$
BEGIN
    RETURN QUERY 
	SELECT 
	v.week_day::text,
	tr.time_range::text,
	COUNT(*)::bigint as count_comments
	FROM (
	    SELECT 
	    (SELECT day_of_week_str FROM public.get_week_day(p.comment_date)) as week_day,
	    CASE 
	        WHEN EXTRACT(MINUTE FROM p.comment_date) >= 30 THEN 
	            TO_CHAR(date_trunc('hour', p.comment_date) + INTERVAL '0.5 hour', 'HH24:MI')
	        ELSE 
	            TO_CHAR(date_trunc('hour', p.comment_date), 'HH24:MI')
	    END as rounded_time
	    FROM public.get_comments_or_pull_requests(
		    commented_by_param,
		    created_by_param,
		    reviewed_by_param,
		    target_branch_param,
		    type_param,
		    from_date_param,
		    to_date_param,
		    repository_param
	    ) p
	    where comment_date is not null
	) v
	LEFT JOIN public.get_timeranges('07:00', '20:00', 30) tr ON public.is_time_in_timerange(v.rounded_time::TEXT, tr.time_range::TEXT) 
	group by 
	v.week_day,
	tr.time_range
	order by v.week_day;
END;
$$ LANGUAGE plpgsql;



DROP FUNCTION IF EXISTS get_merge_time_by_complexity;

CREATE OR REPLACE FUNCTION get_merge_time_by_complexity(
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text,
    merge_time_param text
) RETURNS TABLE (
	pr_id text,
	created_by_name text,
    merge_time float,
    count_changes bigint,
    count_changes_delta bigint
) AS $$
BEGIN
    RETURN QUERY 
    SELECT DISTINCT
	p.pr_id::text as pr_id,
	p.created_by_name::text as created_by_name,
	p.merge_time::float as merge_time,
	(p.count_inserted_lines + p.count_deleted_lines)::bigint as count_changes,
	(p.count_inserted_lines - p.count_deleted_lines)::bigint as count_changes_delta
	FROM public.get_comments_or_pull_requests(
	    commented_by_param,
	    created_by_param,
	    reviewed_by_param,
	    target_branch_param,
	    type_param,
	    from_date_param,
	    to_date_param,
	    repository_param,
	    merge_time_param
	) p
	WHERE p.count_inserted_lines > 0 or p.count_deleted_lines > 0;
END;
$$ LANGUAGE plpgsql;





DROP FUNCTION IF EXISTS get_summary_statistics_by_day;
CREATE OR REPLACE FUNCTION get_summary_statistics_by_day(
    aggregation_period INTERVAL,
    percentile double precision,
    date_ref text,
    commented_by_param text,
    created_by_param text,
    reviewed_by_param text,
    target_branch_param text,
    type_param text,
    from_date_param text,
    to_date_param text,
    repository_param text
) RETURNS TABLE (
    day date,
    nb_pull_requests double precision,
    nb_comments_by_pr double precision,
    comments_length_by_pr bigint,
    first_comment_delay double precision,
    merge_time double precision,
    count_changed_lines double precision,
    count_delta_changed_lines double precision
) AS $$
DECLARE
    interval_in_days FLOAT;
BEGIN
    interval_in_days := EXTRACT(EPOCH FROM aggregation_period) / (24 * 60 * 60) - 1;

    RETURN QUERY
    WITH values AS (
	    SELECT 
	        days.date AS day,
	        days.num_day as num_day,
	        p.pr_id,
			(count(distinct p.comment_id)::FLOAT) / nullif(count(distinct p.pr_id), 0) AS nb_comments_by_pr,
			sum(COALESCE(p.comment_length,0)) / nullif(count(distinct p.pr_id), 0) AS comments_length_by_pr,
	        p.merge_time,
	        p.first_comment_delay,
	        p.count_inserted_lines,
	        p.count_deleted_lines
	    FROM (
	    	select d.*, row_number() over(order by date) as num_day
	    	from public.get_dates(from_date_param, to_date_param) d
			WHERE NOT d.is_weekend
	    ) days
	    LEFT JOIN public.get_comments_or_pull_requests(
	        commented_by_param,
	        created_by_param,
	        reviewed_by_param,
	        target_branch_param,
	        type_param,
	        NULL,
	        NULL,
	        repository_param
		) p ON days.date = (
	        CASE
	            WHEN 'completion' = date_ref THEN completion_date::DATE
	            ELSE creation_date::DATE
	        END
	    )
	    group by 
	    p.pr_id,
	    days.date,
	    days.num_day,
	    p.merge_time,
	    p.first_comment_delay,
	    p.count_inserted_lines,
	    p.count_deleted_lines
	)
	SELECT DISTINCT
	    outer_dv.day,
	    (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.nb_pull_requests::float) 
	     FROM (
			select 
            values.num_day as num_day,
			values.day,
			count(values.pr_id)::float as nb_pull_requests
			from values
			group by values.num_day, values.day
	     ) AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::float as nb_pull_requests,
	     (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.nb_comments_by_pr) 
	     FROM values AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::float as nb_comments_by_pr,
	     (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.comments_length_by_pr) 
	     FROM values AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::bigint as comments_length_by_pr,
	    (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.first_comment_delay) 
	     FROM values AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::float as first_comment_delay,
	    (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.merge_time) 
	     FROM values AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::float as merge_time_delay,
	    (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.count_inserted_lines + inner_dv.count_deleted_lines) 
	     FROM values AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::float as count_changed_lines,
	    (SELECT PERCENTILE_CONT(percentile) WITHIN GROUP (ORDER BY inner_dv.count_inserted_lines - inner_dv.count_deleted_lines) 
	     FROM values AS inner_dv 
	     WHERE inner_dv.num_day BETWEEN outer_dv.num_day - interval_in_days AND outer_dv.num_day)::float as count_delta_changed_lines
	FROM values AS outer_dv;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_developers(start_date TEXT, end_date TEXT) 
RETURNS TABLE (name VARCHAR) AS $$ 
BEGIN 
    RETURN QUERY 
    SELECT DISTINCT d.name 
    FROM ( 
        SELECT DISTINCT developer_id 
        FROM public.comments 
        LEFT JOIN pull_requests pr ON pr.id = comments.pull_request_id 
        WHERE pr.completion_date BETWEEN start_date::TIMESTAMP AND end_date::TIMESTAMP

        UNION 

        SELECT DISTINCT pr.created_by_id AS developer_id 
        FROM public.pull_requests pr 
        WHERE pr.completion_date BETWEEN start_date::TIMESTAMP AND end_date::TIMESTAMP

        UNION 

        SELECT DISTINCT pr_approvers.approver_id AS developer_id 
        FROM public.pull_requests pr 
        LEFT JOIN pull_request_approvers pr_approvers ON pr_approvers.pull_request_id = pr.id 
        WHERE pr.completion_date BETWEEN start_date::TIMESTAMP AND end_date::TIMESTAMP 

        UNION 

        SELECT DISTINCT ft.developer_id AS developer_id 
        FROM public.features ft 
        WHERE ft.date BETWEEN start_date::TIMESTAMP AND end_date::TIMESTAMP 
    ) devs 
    LEFT JOIN public.developers d ON d.id = devs.developer_id 
    WHERE devs.developer_id  is NOT NULL
    ORDER BY name; 
END; 
$$ LANGUAGE plpgsql;