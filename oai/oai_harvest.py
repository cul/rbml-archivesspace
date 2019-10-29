from configparser import ConfigParser
import subprocess
import os


# Script to harvest batches of OAI data from ArchivesSpace, using pyoaiharvester (https://github.com/vphill/pyoaiharvester).  


# Set to True to harvest from Dev, False to use Prod.
dev = True


# Set to path of pyoaiharvest.py script.
my_path = os.path.dirname(__file__)
harvester_path = os.path.join(my_path,'pyoaiharvester/pyoaiharvest.py')
config_path = os.path.join(my_path, 'config.ini')
config = ConfigParser()
config.read(config_path)


if dev == True:
    oaiURL = config['DEV']['baseOAIURL']
    oaiPrefix = config['DEV']['oaiPrefix']
else:
    oaiURL = config['PROD']['baseOAIURL']
    oaiPrefix = config['PROD']['oaiPrefix']


# Set the type of output, eg., oai_dc, oai_marc, oai_ead. 

theOutputType = 'oai_marc'


# Set from and to date. If not using, remove from cmd below. 
# TODO: allow full range of optional parameters.
fromDate = '20180701'
toDate = '20180801'

# Where it goes.
outFile = 'output_file_name.xml'


cmd = 'python ' + harvester_path + ' -l ' + oaiURL +  ' -m ' + theOutputType + ' -s collection' + ' -o ' + outFile + ' -f ' + fromDate + ' -u ' + toDate


# This will always work but is kludgy.
subprocess.call(cmd, shell=True)



