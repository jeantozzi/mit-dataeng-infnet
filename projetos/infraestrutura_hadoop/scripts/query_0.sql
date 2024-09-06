USE imdb;
DROP TABLE IF EXISTS top_titles;
CREATE TABLE top_titles AS
    (
        SELECT 
            t.tconst,
            t.primaryTitle,
            r.averageRating,
            r.numVotes,
            t.startYear,
            t.titleType,
            t.runtimeMinutes
        FROM rating AS r 
        INNER JOIN title AS t 
        USING(tconst) 
        ORDER BY numVotes DESC 
        LIMIT 250
    );

SELECT * FROM top_titles;