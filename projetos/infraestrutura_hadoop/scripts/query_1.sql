USE imdb;
SELECT 
    CAST(FLOOR(startYear / 10) * 10 AS INT) AS decade,
    titleType,
    COUNT(*) AS count
FROM top_titles
WHERE startYear IS NOT NULL
GROUP BY FLOOR(startYear / 10) * 10, titleType
ORDER BY FLOOR(startYear / 10) * 10 DESC, titleType DESC;