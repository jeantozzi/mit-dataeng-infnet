USE imdb;
WITH translation_counts AS (
    SELECT
        titleId AS tconst,
        COUNT(*) AS translation_count
    FROM
        title_translation
    GROUP BY
        titleId
)

SELECT
    ROUND(AVG(tc.translation_count)) AS avg_translations
FROM
    top_titles tt
INNER JOIN
    translation_counts tc ON tt.tconst = tc.tconst;
