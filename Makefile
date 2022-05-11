DBFOLDER := dbs
DUCKDB := $(DBFOLDER)/fungid.ddb
IMAGES := $(DBFOLDER)/images
DOWNLOADED := $(IMAGES)/downloaded
VALIDATED := $(IMAGES)/validated
CONVERTED := $(IMAGES)/converted
CONVERTEDRECORD := $(IMAGES)/converted-record.csv
VALID500 := $(IMAGES)/500


download-images: validate-downloads
	mkdir -p $(DOWNLOADED)

	awk '{ if(length($$4) == 0) {e="jpg"} else {e=$$4} print "$(DOWNLOADED)/" $$2 "-" $$1 "." e " " $$5}' $(DBFOLDER)/multimedia-numbered.txt \
		| xargs -P 32 -L1 bash -c 'wget -c --tries=10 $$1 -O $$0'

validate-downloads:
	ls -f1 $(DOWNLOADED) | parallel "identify -regard-warnings $(DOWNLOADED)/{} > /dev/null && mv $(DOWNLOADED)/{} $(VALIDATED)/{} || rm $(DOWNLOADED)/{}" 

resize-images:
	ls -f1 $(VALIDATED) |\
		parallel -j16 "\
			convert $(VALIDATED)/{} -resize '500x>' $(VALID500)/{.}.png \
				&& mv $(VALIDATED)/{} $(CONVERTED)/"

register-converted:
	find $(CONVERTED) -type f | grep -o '[0-9]\+\-[0-9]\+' | tr '-' ',' >> $(CONVERTEDRECORD) \
		&& sort $(CONVERTEDRECORD) | uniq > $(CONVERTEDRECORD).tmp && mv $(CONVERTEDRECORD).tmp $(CONVERTEDRECORD) \
		&& duckdb $(DUCKDB) -cmd "DROP TABLE converted;" "CREATE TABLE converted (gbifid BIGINT, imgid INTEGER);" \
		&& duckdb $(DUCKDB) "COPY converted FROM '$(CONVERTEDRECORD)';" \
		&& duckdb $(DUCKDB) "SELECT COUNT(*) FROM converted;" \
		&& mv $(CONVERTED) $(CONVERTED)-`date +'%y-%m-%d-%H%M-%S'` \
		&& mkdir $(CONVERTED)

sync-external-hd:
	rsync -au --inplace $(CONVERTED)-22-05-11-1422-14 /Volumes/External/fungid/images/converted-22-05-11-1422-14

start-downloads: #validate-downloads resize-images register-converted
		duckdb $(DUCKDB) -cmd ".mode csv" ".separator '	'" ".headers off" "SELECT CAST(m.gbifid AS VARCHAR) || '-' || CAST(m.imgid AS VARCHAR) || '.' || format as filename, identifier \
			FROM multimedia m \
			LEFT JOIN converted c ON c.gbifid = m.gbifid AND c.imgid = m.imgid \
			WHERE c.gbifid IS NULL LIMIT 10;" \
		| tr -d '\r' \
		| xargs -P 32 -L1 bash -c 'wget -c --tries=10 $$1 -O $(DOWNLOADED)/$$0'

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
    
rename-files:
	cd $(DOWNLOADED) && ls -f1 | rename -v 's/jpeg/jpg/' && ls -f1 | rename -v 's/JPG/jpg/' && ls -f1 | rename -v 's/php.*/jpg/'

#Temp
move-converted:
	ls -f1 $(VALIDATED) | parallel "if [ -f $(VALID500)/{.}.png ]; then mv $(VALIDATED)/{} $(CONVERTED)/{}; fi;"
