DBFOLDER := dbs
DUCKDB := $(DBFOLDER)/fungid.ddb
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
EXTERNAL := /Volumes/External/fungid

start-downloads: validate-downloads resize-images register-converted register-errors download

download: 
		duckdb $(DUCKDB) -cmd ".mode csv" ".separator '	'" ".headers off" "SELECT CAST(m.gbifid AS VARCHAR) || '-' || CAST(m.imgid AS VARCHAR) || '.' || format as filename, identifier \
			FROM multimedia m \
			LEFT JOIN converted c ON c.gbifid = m.gbifid AND c.imgid = m.imgid \
			LEFT JOIN errors e ON e.gbifid = m.gbifid AND e.imgid = m.imgid \
			WHERE c.gbifid IS NULL \
			AND e.gbifid IS NULL;" \
		| tr -d '\r' \
		| xargs -P 32 -L1 bash -c 'echo "$$1 |"; wget --read-timeout=10 --connect-timeout=10 -c -nv --tries=2 $$1 -O $(DOWNLOADED)/$$0 || mv $(DOWNLOADED)/$$0 $(DLERRORS)`echo $$?`/$$0'

validate-downloads:
	-ls -f1 $(DOWNLOADED) | parallel "identify -regard-warnings $(DOWNLOADED)/{} > /dev/null && mv $(DOWNLOADED)/{} $(VALIDATED)/{} || mv $(DOWNLOADED)/{} $(ERRORS)/invalid/{}" 

resize-images:
	-ls -f1 $(VALIDATED) |\
		parallel -j16 "\
			convert $(VALIDATED)/{} -resize '500x>' $(VALID500)/{.}.png \
				&& mv $(VALIDATED)/{} $(CONVERTED)/"

register-converted:
	find $(CONVERTED) -type f | grep -o '[0-9]\+\-[0-9]\+' | tr '-' ',' >> $(CONVERTEDRECORD) \
		&& sort $(CONVERTEDRECORD) | uniq > $(CONVERTEDRECORD).tmp && mv $(CONVERTEDRECORD).tmp $(CONVERTEDRECORD) \
		&& duckdb $(DUCKDB) -cmd "DROP TABLE converted;" "CREATE TABLE converted (gbifid BIGINT, imgid INTEGER);" \
		&& duckdb $(DUCKDB) "COPY converted FROM '$(CONVERTEDRECORD)';" \
		&& duckdb $(DUCKDB) "SELECT COUNT(*) FROM converted;" \
		&& mv $(CONVERTED) $(BACKUP)/`date +'%y-%m-%d-%H%M-%S'` \
		&& mkdir $(CONVERTED)

sync-external-hd:
	find $(BACKUP) -type d -maxdepth 1 | parallel "mkdir -p $(EXTERNAL)/{}" \
		&& find $(BACKUP) -type f -exec mv -v {} /Volumes/External/fungid/{} \;


register-errors:
	find $(ERRORS) -type f | grep -o '[a-z0-9]\+\/[0-9]\+\-[0-9]\+' | tr '-' ',' | tr '/' ',' >> $(ERRORRECORD) \
		&& sort $(ERRORRECORD) | uniq > $(ERRORRECORD).tmp && mv $(ERRORRECORD).tmp $(ERRORRECORD) \
		&& find $(ERRORS) -type f -delete \
		&& duckdb $(DUCKDB) -cmd "DROP TABLE errors;" "CREATE TABLE errors (errorCode VARCHAR, gbifid BIGINT, imgid INTEGER);" \
		&& duckdb $(DUCKDB) "COPY errors FROM '$(ERRORRECORD)';" \
		&& duckdb $(DUCKDB) "SELECT errorCode, COUNT(*) FROM errors GROUP BY 1;"		

error-arctos:
	duckdb $(DUCKDB) -cmd ".mode csv" ".separator '	'" ".headers off" "SELECT CAST(m.gbifid AS VARCHAR) || '-' || CAST(m.imgid AS VARCHAR) || '.' || format as filename \
			FROM multimedia m \
			WHERE identifier LIKE 'http://arctos.database.museum/media/%';" \
		| parallel -d "\r\n" "touch $(ERRORS)/arctos/{}"


generate-samples:
	mkdir -p $(CURRENTSAMPLE) \
		&& duckdb $(DUCKDB) -cmd ".mode csv" ".separator '	'" ".headers off" "SELECT CAST(m.gbifid AS VARCHAR) || '-' || CAST(m.imgid AS VARCHAR) || '.png' \
			FROM images m JOIN occurrence o on o.gbifid = m.gbifid WHERE o.institutioncode IN ('DUKE') USING SAMPLE 10000;" \
		| parallel -d "\r\n" "cp $(VALID500)/{} $(CURRENTSAMPLE)/{}"

register-categorized:
	duckdb $(DUCKDB) -cmd "DROP TABLE categorized;" "CREATE TABLE categorized (gbifid VARCHAR, gbifid BIGINT, imgid INTEGER);" \
		&& duckdb $(DUCKDB) "COPY errors FROM '$(ERRORRECORD)';" \
		&& duckdb $(DUCKDB) "SELECT errorCode, COUNT(*) FROM errors GROUP BY 1;"		

generate-trainingimages:
	duckdb $(DUCKDB) -cmd ".mode csv" ".headers off" "SELECT '$(VALID500)/' || t.gbifid || '-' || t.imgid || '.png' \
		FROM trainingimages t  \
		JOIN converted c ON t.gbifid = c.gbifid AND t.imgid = c.imgid" > trainingimages.txt

categorize:
	find $(IMAGES)/224 -type f -name "*.png" | python clean.py

pull-uncertain:
	cat converted-categorized.txt | tr ',' '\t' | awk '{ if ($$3 < .50) { print $$1 }};' | tr -d '\r' | tr -d '█'| parallel cp {} uc/{}

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

