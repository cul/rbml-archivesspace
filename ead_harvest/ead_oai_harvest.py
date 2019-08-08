import ASFunctions as asf
import re
import requests
import secrets
import secretsDev


# Script to harvest a set of EADs from ArchivesSpace, based on lookup of BibID from local source. 1st arg is a plain text file with one BibID per line. 2nd arg is a lookup CSV (repo,asid,bibid). 3rd arg is the output location (a local folder, in which EAD XML files will be written).



# Set to true to test on dev.
dev = False

if dev == True:
    oaiURL = secretsDev.baseOAIURL
    oaiPrefix = secretsDev.oaiPrefix
else:
    oaiURL = secrets.baseOAIURL
    oaiPrefix = secrets.oaiPrefix



def main():

    x = harvestBatchEAD('bibids_test.txt','id_lookup.csv','xml')


    quit()


#############


def harvestBatchEAD(ids_file,lookup_file,out_folder):
    bibidFile = ids_file
    lookupFile = lookup_file
    outFolder = out_folder

    with open(bibidFile) as f: 
        the_bibids = [line.rstrip('\n') for line in f]

    the_errors = []
    the_processed = []

    for a_bibid in the_bibids:
        print('Processing bibid: ' + a_bibid)
        if a_bibid:
            try:
                the_lookup = asf.lookupByBibID(a_bibid,lookupFile)
                the_repo = the_lookup[0]
                the_asid = the_lookup[1]
                the_processed.append(a_bibid)
            except:
                # Can't find in lookup
                the_repo = 0
                the_asid = 0
                the_errors.append(a_bibid)

        # print(the_repo)
        # print(the_asid)

        if (a_bibid and the_asid != 0):
            the_ead = getSingleEAD(the_repo, the_asid)

            the_filepath = outFolder + '/' + a_bibid + '_ead.xml' 
            with open(the_filepath, "w") as myfile:
                myfile.write(the_ead)

    # Report results
    print('Processed ' + str(len(the_processed)) + ' records.')
    if len(the_errors) > 0:
        print('*** Warning: ' + str(len(the_errors)) + ' errors. Could not process id ' + ', '.join(the_errors) + ' ***')




def getSingleEAD(asRepo,asID):
    # Use this for now.
    xmlHead = '<?xml version="1.0" encoding="UTF-8"?>'
    myURL = oaiURL + '?verb=GetRecord&identifier=' + oaiPrefix + '//repositories/' + str(asRepo) + '/resources/' + str(asID) + '&metadataPrefix=oai_ead'
    myResponse = requests.get(myURL)
    myEAD = myResponse.text
    # discard everything up to open record tag (lookahead)
    myEAD = re.sub('.*?(?=<record>)', '\n', myEAD, flags=re.MULTILINE)
    # discard anything following the closing record tag (lookbehind)
    myEAD = re.sub('(?<=</record>).*', '\n', myEAD, flags=re.MULTILINE) 

    #TODO: fix this regex mess!
    myEAD = re.sub('<record>.*<metadata>', '', myEAD, flags=re.MULTILINE) 
    myEAD = re.sub('</metadata>\s*</record>', '', myEAD, flags=re.MULTILINE) 
    myEAD = xmlHead + myEAD

    # fix malformed output
    myEAD = re.sub('& ', '&amp; ', myEAD, re.MULTILINE)

    ## [Add any other sanitization here]
    
    return myEAD


def text_clean(the_str):
    the_str = " ".join(re.split("\s+", the_str, flags=re.UNICODE))
    the_str = re.sub('\s?xmlns=".* *"', '', the_str)
    return the_str




if __name__ == '__main__':
    main()
