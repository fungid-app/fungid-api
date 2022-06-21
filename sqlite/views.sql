DROP VIEW IF EXISTS validobservations;
CREATE VIEW validobservations AS
SELECT * 
FROM observations
WHERE specieskey IS NOT NULL
AND genuskey IS NOT NULL
AND decimallatitude IS NOT NULL
AND decimallongitude IS NOT NULL
AND coordinateuncertaintyinmeters IS NOT NULL;

DROP VIEW IF EXISTS trainingdata;
CREATE VIEW trainingdata AS
SELECT *, 
	CASE 
		WHEN normalized_month < 3 OR normalized_month > 11 THEN 'winter'
		WHEN normalized_month BETWEEN 3 AND 5 THEN 'spring'
		WHEN normalized_month BETWEEN 6 AND 8 THEN 'summer'
		ELSE 'autumn'
	END AS season
FROM (
	SELECT o.gbifid, o."_family", o.genus, o.species,
		strftime('%Y', eventdate) as eventyear, 
		strftime('%m', eventdate) as eventmonth, 
		strftime('%d', eventdate) as eventday, 
		o.eventdate, 
		o.decimallatitude, o.decimallongitude, 
		COALESCE(k.kg, 0) AS kg, COALESCE(g.elu, 0) AS elu,
		v.class1 AS elu_class1, v.class2 AS elu_class2, v.class3 AS elu_class3, 
		((strftime('%m', eventdate) + CASE WHEN decimallatitude < 0 THEN 6 ELSE 0 END) % 12) + 1 AS normalized_month,
		st.imgid
	FROM validobservations o
	LEFT JOIN geo_kg k ON o.gbifid = k.gbifid
	LEFT JOIN geo_gelu g ON o.gbifid = g.gbifid
	LEFT JOIN elu_values v ON g.elu = v.eluid
	JOIN (
		SELECT specieskey
		FROM trainingimages
		GROUP BY 1
	) s ON o.specieskey = s.specieskey
	LEFT JOIN trainingimages st ON o.gbifid = st.gbifid
) a;

DROP VIEW IF EXISTS validimages;
CREATE VIEW validimages AS
SELECT i._type, i.format, i.identifier, i.imgid, v.*
FROM multimedia i
JOIN validobservations v ON i.gbifid  = v.gbifid 
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
JOIN converted c ON c.gbifid = i.gbifid AND c.imgid = i.imgid
WHERE ii.gbifid IS NULL;

DROP VIEW IF EXISTS rankedimages;
CREATE VIEW rankedimages AS 
SELECT r.*, 
	ROW_NUMBER() OVER (PARTITION BY familykey, genuskey, specieskey ORDER BY imgid, gbifid DESC) as rank
FROM (
	SELECT o.gbifid, o.imgid, o."_family", o.genus, o.species, o.familykey, o.genuskey, o.specieskey
	FROM validimages o
) r;

DROP VIEW IF EXISTS imagestodownload;
CREATE VIEW imagestodownload AS
SELECT i.*
FROM images i
JOIN validobservations v ON i.gbifid  = v.gbifid 
LEFT JOIN errors e ON i.imgid = e.imgid AND i.gbifid = e.gbifid AND e.errorCode IN('arctos', 'invalid', 'download8')
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
LEFT JOIN converted c ON c.gbifid = i.gbifid AND c.imgid = i.imgid
WHERE c.gbifid IS NULL
AND ii.gbifid IS NULL
AND e.gbifid IS NULL;

DROP VIEW IF EXISTS trainingimages;
CREATE VIEW trainingimages AS 
SELECT r.gbifid, r.imgid, r."_family", r.genus, r.species, r.familykey, r.genuskey, r.specieskey, r.rank
FROM rankedimages r 
JOIN (
	SELECT o.specieskey
	FROM rankedimages o 
	GROUP BY 1,2,3
	HAVING COUNT(*) > 100
) s ON r.specieskey = s.specieskey
WHERE r.rank < 5000
ORDER BY r.rank;
