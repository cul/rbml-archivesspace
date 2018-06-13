Set up for daily and monthly oai feed

Need to install:<br/>
saxon9he.jar<br/>
python 2.7<br/>
https://pypi.org/project/oaiharvest<br/>
https://github.com/vphill/pyoaiharvester<br/>


Daily script for cron job: <br/>
as_oai.sh <br/>
#this script will pull down the whole AS oai feed and the daily delta, and transform them usind the cleanup scripts.


Notes:
1) Package to download complete OAI feed
For download of individual files:
https://pypi.org/project/oaiharvest/#examples<br/>
oai-harvest https://aspace-dev.library.columbia.edu/oai -p oai_marc

For download into one file:
https://github.com/vphill/pyoaiharvester<br/>
python pyoai.py -l https://aspace-dev.library.columbia.edu/oai -o asAll.xml -m oai_marc
