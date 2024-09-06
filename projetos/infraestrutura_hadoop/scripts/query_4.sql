USE imdb;
WITH director_appearances AS (
    SELECT
        c.tconst,
        director AS nconst
    FROM
        crew c
    LATERAL VIEW explode(c.directors) d AS director
    WHERE
        c.tconst IN (SELECT tconst FROM top_titles)
),
director_count AS (
    SELECT
        da.nconst,
        COUNT(*) AS appearance_count
    FROM
        director_appearances da
    GROUP BY
        da.nconst
)

SELECT
    dc.nconst,
    p.primaryName AS director_name,
    dc.appearance_count,
    CASE 
        WHEN p.deathYear IS NOT NULL THEN 'Deceased'
        ELSE 'Alive'
    END AS status
FROM
    director_count dc
JOIN
    person p ON dc.nconst = p.nconst
ORDER BY
    dc.appearance_count DESC
LIMIT 5;
