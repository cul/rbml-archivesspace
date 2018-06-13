Set up for daily and monthly oai feed

Need to install:
saxon9he.jar
python 2.7
https://pypi.org/project/oaiharvest
https://github.com/vphill/pyoaiharvester


Daily script for cron  job: 
as_oai.sh 
#this script will pull down the whole AS oai feed and the daily delta, and transform them usind the cleanup scripts.


Notes:
1) Package to download complete OAI feed
For download of individual files:
https://pypi.org/project/oaiharvest/#examples
oai-harvest https://aspace-dev.library.columbia.edu/oai -p oai_marc

For download into one file:
https://github.com/vphill/pyoaiharvester
python pyoai.py -l https://aspace-dev.library.columbia.edu/oai -o asAll.xml -m oai_marc
