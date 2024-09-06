-- Criação do database
CREATE DATABASE IF NOT EXISTS imdb;
USE imdb;

-- Criação das tabelas
DROP TABLE IF EXISTS title;
CREATE TABLE title (
    tconst STRING,
    titleType STRING,
    primaryTitle STRING,
    originalTitle STRING,
    isAdult INT,
    startYear INT,
    endYear INT,
    runtimeMinutes INT,
    genres ARRAY<STRING>
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS title_translation;
CREATE TABLE title_translation (
    titleId STRING,
    ordering INT,
    title STRING,
    region STRING,
    language STRING,
    types ARRAY<STRING>,
    attributes ARRAY<STRING>,
    isOriginalTitle INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
COLLECTION ITEMS TERMINATED BY ','
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS episode;
CREATE TABLE episode (
    tconst STRING,
    parentTconst STRING,
    seasonNumber INT,
    episodeNumber  INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
COLLECTION ITEMS TERMINATED BY ','
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS principal;
CREATE TABLE principal (
    tconst STRING,
    ordering INT,
    nconst STRING,
    category STRING,
    job STRING,
    characters STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
COLLECTION ITEMS TERMINATED BY ','
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS crew;
CREATE TABLE crew (
    tconst STRING,
    directors ARRAY<STRING>,
    writers ARRAY<STRING>
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
COLLECTION ITEMS TERMINATED BY ','
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS person;
CREATE TABLE person (
    nconst STRING,
    primaryName STRING,
    birthYear INT,
    deathYear INT,
    primaryProfession ARRAY<STRING>,
    knownForTitles ARRAY<STRING>
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
COLLECTION ITEMS TERMINATED BY ','
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS rating;
CREATE TABLE rating (
    tconst STRING,
    averageRating FLOAT,
    numVotes INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
COLLECTION ITEMS TERMINATED BY ','
MAP KEYS TERMINATED BY ':'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE
TBLPROPERTIES ('skip.header.line.count'='1');

-- Ingestão das tabelas
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/title.basics.tsv' OVERWRITE INTO TABLE title;
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/title.akas.tsv' OVERWRITE INTO TABLE title_translation;
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/title.episode.tsv' OVERWRITE INTO TABLE episode;
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/title.principals.tsv' OVERWRITE INTO TABLE principal;
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/title.crew.tsv' OVERWRITE INTO TABLE crew;
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/name.basics.tsv' OVERWRITE INTO TABLE person;
LOAD DATA INPATH '/user/${hiveconf:USER}/datasets/title.ratings.tsv' OVERWRITE INTO TABLE rating;