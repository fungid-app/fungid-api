-- Duckdb
-- COPY (SELECT phylum, phylumkey fROM occurrence WHERE phylum IS NOT NULL GROUP BY 1,2 ORDER BY 1) TO 'phylum.csv' (DELIMITER ',', HEADER);
-- COPY (SELECT _class, classkey, phylum fROM occurrence WHERE _class IS NOT NULL GROUP BY 1,2, 3 ORDER BY 1) TO 'class.csv' (DELIMITER ',', HEADER);
-- COPY (SELECT _order, orderkey, _class fROM occurrence WHERE _order IS NOT NULL GROUP BY 1,2, 3 ORDER BY 1) TO 'order.csv' (DELIMITER ',', HEADER);
-- COPY (SELECT _family, familykey, _order fROM occurrence WHERE _family IS NOT NULL GROUP BY 1,2, 3 ORDER BY 1) TO 'family.csv' (DELIMITER ',', HEADER);
-- COPY (SELECT genus, genuskey, _family fROM occurrence WHERE genus IS NOT NULL GROUP BY 1,2, 3 ORDER BY 1) TO 'genus.csv' (DELIMITER ',', HEADER);
-- COPY (SELECT species, specieskey, genus fROM occurrence WHERE species IS NOT NULL GROUP BY 1,2, 3 ORDER BY 1) TO 'species.csv' (DELIMITER ',', HEADER);

DROP TABLE IF EXISTS phylum;
DROP TABLE IF EXISTS class;
DROP TABLE IF EXISTS order;
DROP TABLE IF EXISTS family;
DROP TABLE IF EXISTS genus;
DROP TABLE IF EXISTS species;


.mode csv
.import 'api/taxonomy/data/phylum.csv' phylum
.import 'api/taxonomy/data/class.csv' class
.import 'api/taxonomy/data/order.csv' order
.import 'api/taxonomy/data/family.csv' family
.import 'api/taxonomy/data/genus.csv' genus
.import 'api/taxonomy/data/species.csv' species

INSERT INTO taxonomy_phylum (key, name) SELECT phylumkey, phylum FROM phylum;

INSERT INTO taxonomy_classtax (key, name, phylum_id) 
SELECT classkey, _class, p.id
FROM class c
JOIN taxonomy_phylum p ON c.phylum = p.name;

INSERT INTO taxonomy_order (key, name, classtax_id) 
SELECT orderkey, _order, p.id
FROM "order" c
LEFT JOIN taxonomy_classtax p ON c._class = p.name;






DROP TABLE IF EXISTS phylum;
DROP TABLE IF EXISTS class;
DROP TABLE IF EXISTS order;
DROP TABLE IF EXISTS family;
DROP TABLE IF EXISTS genus;
DROP TABLE IF EXISTS species;



CREATE TABLE IF NOT EXISTS "taxonomy_phylum" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL UNIQUE, "key" integer NOT NULL);
CREATE TABLE IF NOT EXISTS "taxonomy_classtax" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL UNIQUE, "key" integer NOT NULL, "phylum_id" bigint NOT NULL REFERENCES "taxonomy_phylum" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "taxonomy_order" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL UNIQUE, "key" integer NOT NULL, "classtax_id" bigint NOT NULL REFERENCES "taxonomy_classtax" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "taxonomy_family" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL UNIQUE, "key" integer NOT NULL, "order_id" bigint NOT NULL REFERENCES "taxonomy_order" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "taxonomy_genus" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL UNIQUE, "key" integer NOT NULL, "family_id" bigint NOT NULL REFERENCES "taxonomy_family" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS "taxonomy_species" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL UNIQUE, "key" integer NOT NULL, "description" text NOT NULL, "genus_id" bigint NOT NULL REFERENCES "taxonomy_genus" ("id") DEFERRABLE INITIALLY DEFERRED);
