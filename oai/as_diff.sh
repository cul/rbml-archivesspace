#!/bin/bash

# Script to extract a single bib ID from two separate 
#    OAI-generated XML files and diff them. 
# Use case: verify that output for an unchanged record 
#    is the same before and after an ArchivesSpace version 
#    update, change to MARC exporter, etc.


# Same variables as in as_daily.sh
appdir=.
datadir=AS_harvest
rbmloairepo=../rbml-archivesspace/oai/
harvestrepo=$appdir/pyoaiharvester

# Update with path to Saxon.
saxon_jar='saxon-9.8.0.12-he.jar'

today=$(date +"%Y%m%d")
# For Testing...
today=20181031

# Same variables as in as_daily.sh
allraw=${today}.asAllRaw.xml
deltaraw=${today}.asDeltaRaw.xml

allclean=${today}.asAllClean.xml
deltaclean=${today}.asDeltaClean.xml



# Extract specified records to check for changes.

# The XSLT used to extract a single record from allRaw file for a given date.
diffXSL=${rbmloairepo}/extract_by_bibid.xsl


# The date from which to pull a record for comparison. 
referenceDate=20181029
#This is the expected output, against which the current output will be compared.


# A record to use as comparison.
theBibID=11749061

diffFile1=$datadir/${referenceDate}.asAllRaw.xml
diffFile2=$datadir/$allraw

referenceOutput=$datadir/${today}_diff_ref.xml
newOutput=$datadir/${today}_diff_new.xml


# Extract old version of record.

echo "Extracting record $theBibID ($referenceOutput) from date $referenceDate ..."

java -cp $saxon_jar net.sf.saxon.Transform -xsl:$diffXSL -o:$referenceOutput -s:$diffFile1 bibid=$theBibID

# Extract new version of record.

echo "Extracting record $theBibID ($newOutput) from date $today ... "

java -cp $saxon_jar net.sf.saxon.Transform -xsl:$diffXSL -o:$newOutput -s:$diffFile2 bibid=$theBibID


# Compare the two files

if  diff $referenceOutput $newOutput ; then

    echo "The two records are identical."
    echo ""

else
   echo "Warning: Output for record $theBibID is different than expected. Review diff output."
   echo ""
fi


