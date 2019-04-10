import ASFunctions as asf
import secrets
import secretsDev
import secretsTest

# Script to harvest a batch of EADs via API using a list of BibIDs and a lookup table.


def main():

    # set to Prod | Dev | Test
    asf.server = 'Test'


    bibid_file = "ead_bibids_20190409.txt"
    lookup_file = "id_lookup_20190409.csv"
    outfile_loc = "ead_as_qc_reports/ead_as_qc_xml_TEST4"


    with open(bibid_file) as f: 
        the_bibids = [line.rstrip('\n') for line in f]

    the_errors = []
    the_processed = []

    for a_bibid in the_bibids:
        print('Processing bibid: ' + a_bibid)
        if a_bibid:
            try:
                the_lookup = asf.lookupByBibID(a_bibid,lookup_file)
                the_repo = the_lookup[0]
                the_asid = the_lookup[1]
                the_processed.append(a_bibid)
            except:
                # Can't find in lookup
                the_repo = 0
                the_asid = 0
                the_errors.append(a_bibid)


        if (a_bibid and the_asid != 0):
            the_ead = asf.getEAD(the_repo, the_asid)

            the_filepath = outfile_loc + '/' + a_bibid + '_ead.xml' 
            
            with open(the_filepath, "w") as myfile:
                myfile.write(the_ead)


    # Report results
    print('Processed ' + str(len(the_processed)) + ' records.')
    if len(the_errors) > 0:
        print('*** Warning: ' + str(len(the_errors)) + ' errors. Could not process id ' + ', '.join(the_errors) + ' ***')




if __name__ == '__main__':
    main()



