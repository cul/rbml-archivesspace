#!/bin/bash

#this script will pull down the whole AS oai feed and the daily delta, and transform them usind the cleanup scripts.

#backup 
cp asAll.xml asAll_bak.xml
cp asDelta.xml asDelta_bak.xml

#set yest variable to yesterday
yest=$(date --date="yesterday" +"%d/%m/%Y")

#download entire OAI file
python pyoai.py -l https://aspace-dev.library.columbia.edu/oai -m oai_marc -o asAll.xml

#download the OAI delta for last day
python pyoai.py -l https://aspace-dev.library.columbia.edu/oai -m oai_marc -f $yest -o asDelta.xml

#run cleanup on big file
java -cp saxon9he.jar net.sf.saxon.Transform -o:asClean.xml -s:asAll.xml -xsl:cleanOAI.xsl

#run cleanup on delta file
java -cp saxon9he.jar net.sf.saxon.Transform -o:asDeltaClean.xml -s:asAll.xml -xsl:cleanOAI.xsl

#run special LTI clean up stylesheet
java -cp saxon9he.jar net.sf.saxon.Transform -o:asCleanLTI.xml -s:asAll.xml -xsl:cleanLTI.xsl

#for acttual LTI submission, manually run MarcEdit XML to MARC21 job.

