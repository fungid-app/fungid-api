DBFOLDER := dbs
DUCKDB := $(DBFOLDER)/fungid.ddb
SQLITEDB := $(DBFOLDER)/fungid.sqlite
IMAGES := $(DBFOLDER)/images
DOWNLOADED := $(IMAGES)/downloaded
VALIDATED := $(IMAGES)/validated
CONVERTED := $(IMAGES)/converted
SAMPLES := $(IMAGES)/samples
CURRENTSAMPLE := $(SAMPLES)/$(shell date +'%y-%m-%d-%H%M-%S')
BACKUP := $(IMAGES)/backup
ERRORS := $(IMAGES)/errors
DLERRORS := $(ERRORS)/download
CONVERTEDRECORD := $(IMAGES)/converted-record.csv
ERRORRECORD := $(IMAGES)/error-record.csv
VALID500 := $(IMAGES)/500
EXTERNALNEW := /Volumes/firecuda/fungid

start-downloads: validate-downloads resize-images register-converted register-errors download

download: 
		duckdb $(DUCKDB) -cmd \
			".mode csv" \
			".separator '	'" \
			".headers off" \
			"SELECT CAST(m.gbifid AS VARCHAR) || '-' || CAST(m.imgid AS VARCHAR) || '.' || format as filename, identifier \
				FROM imagestodownload m;" \
		| tr -d '\r' \
		| xargs -P 32 -L1 bash -c 'wget --read-timeout=10 --connect-timeout=10 -c -nv --tries=2 $$1 -O $(DOWNLOADED)/$$0 || mv $(DOWNLOADED)/$$0 $(DLERRORS)`echo $$?`/$$0'

validate-downloads:
	-ls -f1 $(DOWNLOADED) | parallel "identify -regard-warnings $(DOWNLOADED)/{} > /dev/null && mv $(DOWNLOADED)/{} $(VALIDATED)/{} || mv $(DOWNLOADED)/{} $(ERRORS)/invalid/{}" 

resize-images:
	-ls -f1 $(VALIDATED) |\
		parallel -j16 "\
			convert $(VALIDATED)/{} -resize '500x>' $(VALID500)/{.}.png \
		&& mv $(VALIDATED)/{} $(CONVERTED)/"

resize-to-prod:
	comm -23 <(ls dbs/images/500) <(ls dbs/images/224) --check-order \
		| awk '{print "dbs/images/500/" $0}' \
		| python3 resize.py

register-converted:
	find $(CONVERTED) -type f | grep -o '[0-9]\+\-[0-9]\+' | tr '-' ',' >> $(CONVERTEDRECORD) \
		&& sort $(CONVERTEDRECORD) | uniq > $(CONVERTEDRECORD).tmp && mv $(CONVERTEDRECORD).tmp $(CONVERTEDRECORD) \
		&& duckdb $(DUCKDB) -cmd \
			"DROP TABLE converted;" \
			"CREATE TABLE converted (gbifid BIGINT, imgid INTEGER);" \
			"COPY converted FROM '$(CONVERTEDRECORD)';" \
			"SELECT COUNT(*) FROM converted;" \
		&& mv $(CONVERTED) $(BACKUP)/`date +'%y-%m-%d-%H%M-%S'` \
		&& mkdir $(CONVERTED)

sync-external-hd:
	find $(BACKUP) -type d -maxdepth 1 | parallel "mkdir -p $(EXTERNALNEW)/{}" \
		&& find $(BACKUP)/22-05-13* -type f -exec mv -v {} $(EXTERNALNEW)/{} \;

register-errors:
	find $(ERRORS) -type f | grep -o '[a-z0-9]\+\/[0-9]\+\-[0-9]\+' | tr '-' ',' | tr '/' ',' >> $(ERRORRECORD) \
		&& sort $(ERRORRECORD) | uniq > $(ERRORRECORD).tmp && mv $(ERRORRECORD).tmp $(ERRORRECORD) \
		&& find $(ERRORS) -type f -delete \
		&& duckdb $(DUCKDB) -cmd \
			"DROP TABLE errors;" \
			"CREATE TABLE errors (errorCode VARCHAR, gbifid BIGINT, imgid INTEGER);" \
			"COPY errors FROM '$(ERRORRECORD)';" \
			"SELECT errorCode, COUNT(*) FROM errors GROUP BY 1;"		

generate-samples:
	mkdir -p $(CURRENTSAMPLE) \
		&& duckdb $(DUCKDB) -cmd \
			".mode csv" \
			".separator '	'" \
			".headers off" \
			"SELECT CAST(m.gbifid AS VARCHAR) || '-' || CAST(m.imgid AS VARCHAR) || '.png' \
				FROM validimages m \
				USING SAMPLE 10000;" \
		| parallel -d "\r\n" "cp $(VALID500)/{} $(CURRENTSAMPLE)/{}"

climate-zones:
	mkdir -p $(CURRENTSAMPLE) \
		&& duckdb $(DUCKDB) -cmd \
			".mode csv" \
			".separator ','" \
			".headers off" \
			"SELECT gbifid, decimallatitude, decimallongitude \
			 FROM occurrence\
			 WHERE gbifid NOT IN (SELECT gbifid FROM 'dbs/zones.csv') \
			 ORDER BY gbifid;" \
		| python climate-zones.py

generate-training-data-old:
	duckdb $(DUCKDB) "COPY trainingdata TO 'dbs/training/training-data-v0-2.csv' WITH (HEADER 1, DeLIMITER '	');"

generate-training-data:
	sqlite3 $(SQLITEDB) --cmd ".headers on" ".mode csv" ".once dbs/training/training-data-v0-4.csv" "SELECT * FROM trainingdata;"

save-points:
	duckdb $(DUCKDB) "COPY (SELECT gbifid, o.decimallatitude as lat, o.decimallongitude as long FROM validobservations o) TO 'training/points.csv' (HEADER, DELIMITER ',');"

# Multimedia file conversion
add-row-number:
	awk '{ if($$2 == "StillImage") { if($$1 == pid) {rn+=1;} else {rn=1}; pid=$$1; print rn "\t" $$0 }}' $(DBFOLDER)/multimedia.txt > $(DBFOLDER)/multimedia-numbered.txt

replace-format:
	sed -i '' 's#image/dng#dng#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/jpeg#jpg#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/pjpeg#jpg#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/png#png#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/scan#jpg#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/jpg#jpg#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/gif#gif#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/tiff#tiff#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's#image/bmp#bmp#g' $(DBFOLDER)/multimedia-numbered.txt
	sed -i '' 's/jpeg/jpg/g' $(DBFOLDER)/multimedia-numbered.txt

load-sqlite:
	sqlite3 $(SQLITEDB) < sqlite/tables.sql 
	sqlite3 $(SQLITEDB) < sqlite/views.sql
	sqlite3 $(SQLITEDB) < sqlite/indexes.sql

create-versioned-sqlite:
	sqlite3 $(SQLITEDB) ".dump trainingspecies" | sqlite3 dbs/fungid-v0-4.sqlite
	sqlite3 $(SQLITEDB) ".dump trainingobservations" | sqlite3 dbs/fungid-v0-4.sqlite
	sqlite3 $(SQLITEDB) ".dump trainingimages" | sqlite3 dbs/fungid-v0-4.sqlite
	sqlite3 $(SQLITEDB) ".dump speciesstats" | sqlite3 dbs/fungid-v0-4.sqlite
	
run-api:
	cd classifierapi &&\
		docker build -t fungid-api . &&\
		docker run --rm -it -p 9100:8080 -v "$$(cd ../ && pwd)"/models/v0.4/prod:/var/data/v0.4.1 fungid-api

exec-api:
	cd classifierapi &&\
		docker build -t fungid-api . &&\
		docker run -it -p 9100:8080 -v "$$(cd ../ && pwd)"/models/v0.4/prod:/var/data/v0.4.1 fungid-api bash

test-api:
	http -f POST 0.0.0.0:8000/analyze image0@dbs/images/224/2593822195-1.png lat=52.905696 lon=-1.225849 date=2020-01-01 > out.txt

# Jupyter Lab
jupyter:
	jupyter-lab --ip 0.0.0.0 --NotebookApp.token='' --NotebookApp.password='' 
