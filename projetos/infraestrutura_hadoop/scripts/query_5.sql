USE imdb;
WITH series_info AS (
    SELECT
        t.tconst,
        t.primaryTitle,
        COUNT(DISTINCT e.seasonNumber) AS num_seasons,
        COUNT(*) AS num_episodes,
        MAX(t.runtimeMinutes) AS episode_duration
    FROM
        top_titles t
    LEFT JOIN
        episode e ON t.tconst = e.parentTconst
    WHERE
        t.titleType = 'tvSeries'
    GROUP BY
        t.tconst, t.primaryTitle
)

SELECT
    primaryTitle,
    num_seasons AS total_seasons,
    num_episodes AS total_episodes,
    episode_duration,
    num_episodes * episode_duration AS total_runtime
FROM
    series_info
ORDER BY
    num_episodes * episode_duration DESC;