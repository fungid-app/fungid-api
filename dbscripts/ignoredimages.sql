INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'Bad Publisher'
FROM images i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND i.publisher IN ('Margaret H. Fulford Herbarium, University of Cincinnati (CINC)','Yale University Peabody Museum','University of Colorado Museum of Natural History','Brown University Herbarium','Louisiana State University Herbarium','UiT The Arctic University of Norway','The University of Vermont Pringle Herbarium','Australia''s Virtual Herbarium','University of Graz, Institute of Plant Sciences');

INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'Bad Institution'
FROM images i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND i.institutioncode IN ('TENN', 'IB FRC Komi SC UB RAS');

INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'Bad Collection'
FROM images i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND i.collectionid IN ('355fda57-2668-4dfd-b7b8-0acce4d45271','073ee335-f8b9-472e-8262-a909ff15ff05');

INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'Before 1975 and Preserved Speciment'
FROM images i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND basisofrecord = 'PRESERVED_SPECIMEN'
AND _year < 1975

INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'Preserved Specimen'
FROM images i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND basisofrecord = 'PRESERVED_SPECIMEN'

INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'micros'
FROM categorized i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND category = 'micros' 
AND confidence > .90

INSERT INTO ignoredimages
SELECT i.gbifid, i.imgid, 'sheets'
FROM categorized i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND category = 'sheets' 
AND confidence > .90


SELECT reason, COUNT(*) FROM ignoredimages GROUP BY 1


SELECT SUM(isValid) * 1.0 / COUNT(*) AS pctValid, COUNT(*), c.institutioncode
FROM (
	SELECT CASE WHEN category = 'valid' THEN 1 ELSE 0 END AS isValid, i.*
	FROM categorized c
	JOIN images i ON c.gbifid = i.gbifid AND i.imgid  = c.imgid
	LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
	WHERE ii.gbifid IS NULL
) c
GROUP BY 3
HAVING COUNT(*) > 10
ORDER BY 1, 2 DESC;


SELECT 'dbs/images/500/' || CAST(i.gbifid AS VARCHAR) || '-' || CAST(i.imgid AS VARCHAR) || '.png' as filename, _year, i.identifier  
FROM images i
LEFT JOIN ignoredimages ii ON ii.gbifid = i.gbifid AND i.imgid = ii.imgid 
WHERE ii.gbifid IS NULL
AND institutioncode  = 'Härryda kommun'
ORDER BY 1
