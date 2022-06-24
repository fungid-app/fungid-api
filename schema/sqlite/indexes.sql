CREATE UNIQUE INDEX IF NOT EXISTS categorized_gbifid_imgid ON categorized(gbifid, imgid);
CREATE INDEX IF NOT EXISTS errors_gbifid_imgid ON errors(gbifid, imgid);
CREATE UNIQUE INDEX IF NOT EXISTS converted_gbifid_imgid ON converted(gbifid, imgid);
CREATE INDEX IF NOT EXISTS ignoredimages_gbifid_imgid ON ignoredimages(gbifid, imgid);
CREATE UNIQUE INDEX IF NOT EXISTS multimedia_gbifid_imgid ON multimedia(gbifid, imgid);
CREATE UNIQUE INDEX IF NOT EXISTS geo_kg_gbifid ON geo_kg(gbifid);
CREATE UNIQUE INDEX IF NOT EXISTS geo_gelu_gbifid ON geo_gelu(gbifid);
CREATE UNIQUE INDEX IF NOT EXISTS elu_vlaues_eluid ON elu_values(eluid);
CREATE UNIQUE INDEX IF NOT EXISTS observations_gbifid ON observations(gbifid);
CREATE INDEX IF NOT EXISTS observations_specieskey_latitude_longitutde ON observations(specieskey, decimallatitude, decimallongitude);
CREATE INDEX IF NOT EXISTS observations_family_genus_species ON observations(familykey, genuskey, specieskey);
CREATE INDEX IF NOT EXISTS observations_specieskey ON observations(specieskey);

DROP INDEX IF EXISTS observations_latitude_longitutde;

