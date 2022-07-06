-- Duckdb
-- COPY (SELECT phylum, _class, _order, _family, genus, species, COUNT(*) as obs, MAX(eventdate) AS lastobs FROM occurrence WHERE species IS NOT NULL AND genus IS NOT NULL GROUP BY 1,2,3,4,5,6 ORDER BY 1,2,3,4,5,6) TO 'base-api/taxonomy/data/species.csv' (header, delimiter ',');
-- COPY (SELECT m.gbifid, m.imgid, m.identifier, m.rightsholder, m.creator, m.license FROM validimages m JOIN validobservations v ON m.gbifid = v.gbifid) TO 'base-api/taxonomy/data/tmp/images.csv' (header, delimiter ',');
-- COPY (SELECT gbifid, accessRights, license, _language, rightsHolder, recordedBy, eventDate, decimallatitude, decimallongitude, countrycode, stateProvince, county, municipality, locality, vernacularName, species FROM validobservations) TO 'base-api/taxonomy/data/tmp/observations.csv' (header, delimiter ',');
DROP TABLE IF EXISTS species_temp;
DROP TABLE IF EXISTS images_temp;
DROP TABLE IF EXISTS observations_temp;

.mode csv
.import 'base-api/taxonomy/data/species.csv' species_temp
.import 'base-api/taxonomy/data/tmp/images.csv' images_temp
.import 'base-api/taxonomy/data/tmp/observations.csv' observations_temp


UPDATE species_temp SET obs = b.totalobs
 FROM species_temp t
 JOIN (SELECT species, MAX(lastobs) AS maxobs, MIN(lastobs) firstobs, SUM(obs) aS totalobs FROM species_temp GROUP BY 1 HAVING COUNT(*) > 1)
    b ON t.species = b.species AND t.lastobs = b.maxobs;


DELETE FROM species_temp WHERE rowid IN (
    SELECT t.rowid
    FROM species_temp t
    JOIN (SELECT species, MAX(lastobs) AS maxobs, MIN(lastobs) firstobs, SUM(obs) aS totalobs FROM species_temp GROUP BY 1 HAVING COUNT(*) > 1)
        b ON t.species = b.species AND t.lastobs = b.firstobs
);


INSERT INTO taxonomy_species (
    phylum, 
    classname, 
    "order", 
    family, 
    genus, 
    species, 
    description, 
    included_in_classifier, 
    number_of_observations
) SELECT phylum,_class,_order,_family,genus,species, NULL, False, obs FROM species_temp;

UPDATE taxonomy_species SET phylum = NULLIF(phylum, ''), classname = NULLIF(classname, ''), "order" = NULLIF("order", ''), family = NULLIF(family, ''), genus = NULLIF(genus, ''), species = NULLIF(species, ''), description = NULLIF(description, '');

INSERT INTO taxonomy_commonnames (species_id, language, name)
SELECT s.id, LOWER(_language), LOWER(vernacularName)
FROM observations_temp t
JOIN taxonomy_species s ON t.species = s.species
WHERE _language != '' AND vernacularName != ''
GROUP BY 1,2,3;

SELECT COUNT(*) FROM taxonomy_commonnames;


INSERT INTO observations_gbifobserver (name)
SELECT COALESCE(recordedBy, rightsHolder) FROM observations_temp GROUP BY 1;
SELECT COUNT(*) FROM observations_gbifobserver;

INSERT INTO observations_gbifobservations(
    datecreated,
    gbifid,
    latitude,
    longitude,
    public,
    acces_rights,
    rights_holder,
    recorded_by,
    license,
    countrycode,
    state_province,
    county,
    municipality,
    locality,
    species_id,
    observer_id
)
SELECT eventDate,
    t.gbifid,
    decimallatitude,
    decimallongitude,
    False,
    accessRights,
    rightsHolder,
    recordedBy,
    license,
    countrycode,
    stateProvince,
    county,
    municipality,
    locality,
    s.id,
    o.id
FROM observations_temp t
JOIN observations_gbifobserver o ON COALESCE(recordedBy, rightsHolder) = o.name
JOIN taxonomy_species s ON t.species = s.species;

SELECT COUNT(*) FROM observations_gbifobservations;


INSERT INTO observations_gbifobservationimage (
    imgid,
    external_url,
    rights_holder,
    creator,
    license,
    observation_id,
    is_thumbnail
)
SELECT 
    m.imgid, 
    m.identifier, 
    m.rightsholder, 
    m.creator, 
    m.license,
    t.gbifid,
    False
FROM images_temp m
JOIN observations_gbifobservations t ON m.gbifid = t.gbifid;

SELECT COUNT(*) FROM observations_gbifobservationimage;



DROP TABLE IF EXISTS species_temp;
DROP TABLE IF EXISTS images_temp;
DROP TABLE IF EXISTS observations_temp;

VACUUM;
