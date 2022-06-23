DROP TABLE IF EXISTS trainingimages;
CREATE TABLE trainingimages(gbifid BIGINT, imgid INTEGER, "_family" VARCHAR COLLATE NOCASE, genus VARCHAR COLLATE NOCASE, species VARCHAR COLLATE NOCASE, familykey INTEGER, genuskey INTEGER, specieskey INTEGER, rank INTEGER);

INSERT INTO trainingimages(gbifid, imgid, "_family", genus, species, familykey, genuskey, specieskey, rank)
SELECT r.gbifid, r.imgid, r."_family", r.genus, r.species, r.familykey, r.genuskey, r.specieskey, r.rank
FROM rankedimages r 
JOIN (
	SELECT o.specieskey
	FROM rankedimages o 
	WHERE imgid <= 5
	GROUP BY 1
	HAVING COUNT(*) > 100
) s ON r.specieskey = s.specieskey
WHERE r.rank < 5000
AND r.imgid <= 5
ORDER BY r.rank;

DROP TABLE trainingspecies;
CREATE TABLE trainingspecies("_family" VARCHAR COLLATE NOCASE, genus VARCHAR COLLATE NOCASE, species VARCHAR COLLATE NOCASE, 
	familykey INTEGER, genuskey INTEGER, specieskey INTEGER PRIMARY KEY);
INSERT INTO trainingspecies ("_family", genus, species, familykey, genuskey, specieskey)
SELECT "_family", genus, species, familykey, genuskey, specieskey 
FROM trainingimages o
-- Note: with this we are dropping otu ~ 15 qualified species because they have no "family"
WHERE familykey IS NOT NULL 
AND genuskey IS NOT NULL
GROUP BY 1,2,3,4,5,6;


DROP TABLE IF EXISTS trainingobservations;
CREATE TABLE trainingobservations(gbifid BIGINT, 
	"_family" VARCHAR COLLATE NOCASE, genus VARCHAR COLLATE NOCASE, species VARCHAR COLLATE NOCASE, 
	familykey INTEGER, genuskey INTEGER, specieskey INTEGER,
	eventyear INTEGER, eventmonth INTEGER, eventday INTEGER, eventdate TIMESTAMP,
	decimallatitude DOUBLE, decimallongitude DOUBLE,
	kg INTEGER, elu INTEGER, elu_class1 VARCHAR COLLATE NOCASE, elu_class2 VARCHAR COLLATE NOCASE, elu_class3 VARCHAR COLLATE NOCASE,
	normalizedmonth INTEGER, season VARCHAR COLLATE NOCASE
);

INSERT INTO trainingobservations(gbifid,  
	"_family", genus, species, 
	familykey, genuskey, specieskey,
	eventyear, eventmonth, eventday, eventdate, 
	decimallatitude, decimallongitude, 
	kg, elu, elu_class1, elu_class2, elu_class3,
	normalizedmonth, season)
SELECT gbifid,  
	"_family", genus, species, 
	familykey, genuskey, specieskey,
	eventyear, eventmonth, eventday, eventdate, 
	decimallatitude, decimallongitude, 
	kg, elu, elu_class1, elu_class2, elu_class3,
	normalizedmonth, 
	CASE 
		WHEN normalizedmonth < 3 OR normalizedmonth > 11 THEN 'winter'
		WHEN normalizedmonth BETWEEN 3 AND 5 THEN 'spring'
		WHEN normalizedmonth BETWEEN 6 AND 8 THEN 'summer'
		ELSE 'autumn'
	END AS season
FROM (
	SELECT o.gbifid, o."_family", o.genus, o.species, o.familykey, o.genuskey, o.specieskey,
		strftime('%Y', eventdate) as eventyear, 
		strftime('%m', eventdate) as eventmonth, 
		strftime('%d', eventdate) as eventday, 
		o.eventdate, 
		o.decimallatitude, o.decimallongitude, 
		COALESCE(k.kg, 0) AS kg, COALESCE(g.elu, 0) AS elu,
		v.class1 AS elu_class1, v.class2 AS elu_class2, v.class3 AS elu_class3, 
		((strftime('%m', eventdate) + CASE WHEN decimallatitude < 0 THEN 6 ELSE 0 END) % 12) + 1 AS normalizedmonth
	FROM validobservations o
	LEFT JOIN geo_kg k ON o.gbifid = k.gbifid
	LEFT JOIN geo_gelu g ON o.gbifid = g.gbifid
	LEFT JOIN elu_values v ON g.elu = v.eluid
	JOIN trainingspecies s ON o.specieskey = s.specieskey
) a;


DROP VIEW IF EXISTS trainingdata;
CREATE VIEW trainingdata AS
SELECT o.*, st.imgid
FROM trainingobservations o 
LEFT JOIN trainingimages st ON o.gbifid = st.gbifid;


DROP TABLE IF EXISTS speciesstats;
CREATE TABLE speciesstats(
	species INTEGER, 
	stat VARCHAR COLLATE NOCASE, 
	value VARCHAR COLLATE NOCASE, 
	likelihood FLOAT,
	PRIMARY KEY (species, stat, value)
);


INSERT INTO speciesstats (species, stat, value, likelihood) 
WITH stats AS (
	SELECT species, 'kg' as stat, kg as value, COUNT(1) as num
	FROM trainingobservations o
	GROUP BY 1,2,3
	UNION
	SELECT species, 'elu_class1', elu_class1, COUNT(1)
	FROM trainingobservations o
	GROUP BY 1,2,3
	UNION
	SELECT species, 'elu_class2', elu_class2, COUNT(1)
	FROM trainingobservations o
	GROUP BY 1,2,3
	UNION
	SELECT species, 'elu_class3', elu_class3, COUNT(1)
	FROM trainingobservations o
	GROUP BY 1,2,3
	UNION
	SELECT species, 'normalizedmonth', normalizedmonth, COUNT(1)
	FROM trainingobservations o
	GROUP BY 1,2,3
	UNION
	SELECT species, 'season', season, COUNT(1)
	FROM trainingobservations o
	GROUP BY 1,2,3
)
SELECT s.species, s.stat, s.value, (s.num * 1.0) / ss.max_num
FROM stats s
JOIN (
	SELECT species, stat, MAX(num) as max_num
	FROM stats 
	GROUP BY 1, 2
) ss ON s.species = ss.species AND s.stat = ss.stat;


SELECT s.species, s.stat, s.value, s.likelihood 
FROM speciesstats s 
WHERE species = ?
AND (
	(stat = 'kg' AND value = ?)
	OR (stat = 'elu_class1' AND value = ?)
	OR (stat = 'elu_class2' AND value = ?)
	OR (stat = 'elu_class3' AND value = ?)
	OR (stat = 'normalizedmonth' AND value = ?)
	OR (stat = 'season' AND value = ?)
)

SELECT * FROM elu_values ev LIMIT 1

SELECT class1, class2, class3 FROM elu_values WHERE eluid = 222
