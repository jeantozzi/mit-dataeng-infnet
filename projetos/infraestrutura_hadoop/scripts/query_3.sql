USE imdb;
WITH actor_appearances AS (
    SELECT
        pr.nconst AS actor_id,
        p.primaryName AS actor_name,
        COUNT(*) AS appearance_count
    FROM
        principal pr
    JOIN
        top_titles tt ON pr.tconst = tt.tconst
    JOIN
        person p ON pr.nconst = p.nconst
    WHERE
        pr.category in ('actor', 'actress')
    GROUP BY
        pr.nconst, p.primaryName
)

SELECT
    actor_name,
    appearance_count
FROM
    actor_appearances
ORDER BY
    appearance_count DESC
LIMIT 10;
