
CREATE TABLE multimedia AS SELECT * FROM read_csv_auto('dbs/multimedia-numberedvd.txt', SEP='\t', header=True, normalize_names=True, quote='|', sample_size=300000);

CREATE TABLE occurrence AS SELECT * FROM read_csv_auto('dbs/occurrence.txt', SEP='\t', header=True, normalize_names=True, quote='}', sample_size=3000000);


DROP TABLE converted;
CREATE TABLE converted (gbifid BIGINT, imgid INTEGER);
CREATE UNIQUE INDEX converted_idx ON converted(gbifid, imgid);