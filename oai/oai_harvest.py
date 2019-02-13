import secretsDev
import secrets
import subprocess

# Script to harvest batches of OAI data from ArchivesSpace, using pyoaiharvester (https://github.com/vphill/pyoaiharvester).  


# Set to path of pyoaiharvest.py script.
harvester_path = 'pyoaiharvester/pyoaiharvest.py'

# Set to true to harvest from dev.
dev = True

if dev == True:
    oaiURL = secretsDev.baseOAIURL
    oaiPrefix = secretsDev.oaiPrefix
else:
    oaiURL = secrets.baseOAIURL
    oaiPrefix = secrets.oaiPrefix


# Set the type of output, eg., oai_dc, oai_marc, oai_ead. 

theOutputType = 'oai_marc'


# Set from and to date. If not using, remove from cmd below. 
# TODO: allow full range of optional parameters.
fromDate = '20180701'
toDate = '20180801'

# Where it goes.
outFile = 'output_file_name.xml'


cmd = harvester_path + ' -l ' + oaiURL +  ' -m ' + theOutputType + ' -s collection' + ' -o ' + outFile + ' -f ' + fromDate + ' -u ' + toDate


# This will always work but is kludgy.
subprocess.call(cmd, shell=True)



