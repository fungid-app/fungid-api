
--CREATE TABLE multimedia AS SELECT * FROM read_csv_auto('dbs/multimedia-numberedvd.txt', SEP='\t', header=True, normalize_names=True, quote='|', sample_size=300000);

--CREATE TABLE occurrence AS SELECT * FROM read_csv_auto('dbs/occurrence.txt', SEP='\t', header=True, normalize_names=True, quote='}', sample_size=3000000);

--DROP TABLE ignoredimages; 
--CREATE TABLE ignoredimages (gbifid BIGINT, imgid INTEGER, reason VARCHAR);

CREATE TABLE elu AS SELECT * FROM read_csv_auto('dbs/geospatial/globalelu/elu-values.csv', header=True);

CREATE OR REPLACE VIEW images AS 
SELECT m._type, m.format, m.identifier, m.imgid, o.* 
FROM multimedia m 
JOIN occurrence o ON o.gbifid = m.gbifid;


CREATE OR REPLACE VIEW validobservations AS
SELECT * 
FROM occurrence
WHERE specieskey IS NOT NULL
AND genuskey IS NOT NULL
AND decimallatitude IS NOT NULL
AND decimallongitude IS NOT NULL
AND coordinateuncertaintyinmeters IS NOT NULL;


CREATE OR REPLACE VIEW validimages AS
SELECT i.*
FROM images i
JOIN validobservations v ON i.gbifid  = v.gbifid 
JOIN converted c ON c.gbifid = i.gbifid AND c.imgid = i.imgid;

CREATE OR REPLACE VIEW imagestodownload AS
SELECT i.*
FROM images i
JOIN validobservations v ON i.gbifid  = v.gbifid 
LEFT JOIN errors e ON i.imgid = e.imgid AND i.gbifid = e.gbifid AND e.errorCode IN('arctos', 'invalid', 'download8')
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
LEFT JOIN converted c ON c.gbifid = i.gbifid AND c.imgid = i.imgid
WHERE c.gbifid IS NULL
AND ii.gbifid IS NULL
AND e.gbifid IS NULL;




SELECT errorCode, COUNT(*) FROM errors GROUP BY 1;

SELECT COUNT(*) FROM imagestodownload 

DELETE FROM errors WHERE rowid IN (
	SELECT e.rowid
	FROM errors e 
	JOIN errors c ON e.gbifid = c.gbifid AND e.imgid = c.imgid
	WHERE e.errorCode = 'invalid'
	AND c.errorCode  IN ('download8', 'arctos')
)


	
CREATE OR REPLACE VIEW localobservations AS
SELECT o.* 
FROM validobservations o
WHERE decimallatitude BETWEEN 49.8 AND 60.9
AND decimallongitude BETWEEN -10.9 AND 1.8;


SELECT *
FROM validimages m
LEFT JOIN converted c ON c.gbifid = m.gbifid AND c.imgid = m.imgid
WHERE c.gbifid IS NULL

CREATE OR REPLACE VIEW localimages AS
SELECT i.*
FROM validimages i
JOIN localobservations c ON c.gbifid = i.gbifid


CREATE OR REPLACE VIEW rankedimages AS 
SELECT r.*, 
	ROW_NUMBER() OVER (PARTITION BY r.familykey, r.genuskey, r.specieskey ORDER BY r.score, r._year DESC, r.gbifid DESC) as rank
FROM (
	SELECT o.gbifid, o.imgid, o."_family", o.genus, o.species, o.familykey, o.genuskey, o.specieskey, o._year,
		 COALESCE(lo.score, 1) + COALESCE(c.score, 3) + o.imgid * 2 AS score,
	FROM validimages o
	LEFT JOIN (
		SELECT 0 AS score, gbifid FROM localobservations
	) lo ON lo.gbifid = o.gbifid
	-- Preference images already downloaded 
	LEFT JOIN (
		SELECT 0 AS score, gbifid, imgid FROM converted
	) c ON o.imgid = c.imgid AND o.gbifid = c.gbifid
) r;


CREATE OR REPLACE VIEW trainingimages AS 
SELECT r.gbifid, r.imgid, r."_family", r.genus, r.species, r.familykey, r.genuskey, r.specieskey, r.rank
FROM rankedimages r 
JOIN (
	SELECT o.familykey, o.genuskey, o.specieskey
	FROM rankedimages o 
	GROUP BY 1,2,3
	HAVING COUNT(*) > 100
) s ON r.familykey = s.familykey AND r.genuskey = s.genuskey AND r.specieskey = s.specieskey
WHERE r.rank < 1000
ORDER BY r.rank;


SELECT COUNT(*), coordinateuncertaintyinmeters  
FROM validobservations o
GROUP BY 2
ORDER BY 1 DESC

SELECT * FROM occurrence LIMIT 1


SELECT COUNT(*), SUM(CASE WHEN c.gbifid IS NULL THEN 1 ELSE 0 END)
FROM trainingimages t 
LEFT JOIN converted c ON t.gbifid = c.gbifid AND t.imgid = c.imgid 

SELECT t.gbifid || '-' || t.imgid || '.png'
FROM trainingimages t 
JOIN converted c ON t.gbifid = c.gbifid AND t.imgid = c.imgid 

SELECT COUNT(*) FROM validobservations

SELECT COUNT(*) FROM validimages v 

SELECT COUNT(*) 
FROM trainingimages ti 
LEFT JOIN converted c ON ti.gbifid = c.gbifid AND ti.imgid = c.imgid 
WHERE c.gbifid IS NULL

SELECT COUNT(*) FROM trainingimages 

SELECT COUNT(*) FROM rankedimages 


SELECT COUNT(*)
FROM validimages m 
LEFT JOIN converted c ON c.gbifid = m.gbifid AND c.imgid = m.imgid
WHERE c.gbifid IS NULL

SELECT COUNT(*)  FROM occurrence  where decimallongitude  IS NULL

COPY (SELECT gbifid, o.decimallatitude, o.decimallongitude  FROM validobservations o) TO 'points.csv' (HEADER, DELIMITER ','); 