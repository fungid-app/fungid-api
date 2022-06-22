DROP VIEW IF EXISTS validobservations;
CREATE VIEW validobservations AS
SELECT * 
FROM observations
WHERE specieskey IS NOT NULL
AND genuskey IS NOT NULL
AND decimallatitude IS NOT NULL
AND decimallongitude IS NOT NULL
AND coordinateuncertaintyinmeters IS NOT NULL;

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

