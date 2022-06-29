ATTACH DATABASE 'dbs/fungid-v0-4.sqlite' AS pdb;



DROP TABLE IF EXISTS pdb.elu_values;

CREATE TABLE pdb.elu_values(eluid INTEGER PRIMARY KEY, class1 VARCHAR COLLATE NOCASE, class2 VARCHAR COLLATE NOCASE, class3 VARCHAR COLLATE NOCASE);
INSERT INTO pdb.elu_values(eluid, class1, class2, class3)
SELECT eluid, class1, class2, class3
FROM elu_values;



DROP TABLE IF EXISTS pdb.species;

CREATE TABLE pdb.species("_family" VARCHAR COLLATE NOCASE, genus VARCHAR COLLATE NOCASE, species VARCHAR COLLATE NOCASE, 
	familykey INTEGER, genuskey INTEGER, specieskey INTEGER, total INTEGER, PRIMARY KEY(specieskey, species, total));
INSERT INTO species ("_family", genus, species, familykey, genuskey, specieskey, total)
SELECT v."_family", v.genus, v.species, v.familykey, v.genuskey, v.specieskey, COUNT(DISTINCT v.gbifid)
FROM (
	SELECT specieskey
	FROM trainingimages o
	GROUP BY 1
) i
JOIN validobservations v ON i.specieskey = v.specieskey
-- Note: with this we are dropping otu ~ 15 qualified species because they have no "family"
WHERE familykey IS NOT NULL 
AND genuskey IS NOT NULL
GROUP BY 1,2,3,4,5,6;



DROP TABLE IF EXISTS pdb.speciesstats;
CREATE TABLE pdb.speciesstats(
	species INTEGER, 
	stat VARCHAR COLLATE NOCASE, 
	value VARCHAR COLLATE NOCASE, 
	likelihood FLOAT,
	PRIMARY KEY (species, stat, value)
);

INSERT INTO pdb.speciesstats (species, stat, value, likelihood) 
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




DROP TABLE IF EXISTS pdb.observations;

CREATE TABLE pdb.observations(gbifid BIGINT, specieskey INTEGER, decimallatitude DOUBLE, decimallongitude DOUBLE, PRIMARY KEY(specieskey, decimallatitude, decimallongitude));
INSERT INTO pdb.observations(gbifid, specieskey, decimallatitude, decimallongitude)
SELECT gbifid, specieskey, decimallatitude, decimallongitude
FROM trainingobservations;



VACUUM;