# Script to update all extrefs within a given resource, e.g., to add xlink namespace not permitted in the Harvard Excel importer.

import ASFunctions as asf
import json
import re


def main():
    # Test functions here.

    from pprint import pprint

    server = 'Test'
    asf.setServer(server)

    # The resource to scan
    the_resource = (4,6288)

    # A place to put output of saved json objects (optional)
    output_folder = 'output/replace_extrefs'


    # Retrieve all archival objects under a given resource
    x = asf.getResponse('/repositories/' + str(the_resource[0]) + '/resources/' + str(the_resource[1]) + '/ordered_records')
    y = json.loads(x)['uris']

    # Select only the ones that are items or files, and add to a list
    the_refs = [ r['ref'] for r in y if r['level'] in ['item','file'] ]

    cnt = 0

    for a_ref in the_refs:
        ref_decomposed = a_ref.split('/')
        repo, asid = ref_decomposed[2], ref_decomposed[4] 

        ref_json = asf.getArchivalObject(repo,asid)

        out_path = output_folder + '/' + str(repo) + '_' + str(asid) + '.json'


        data_old = ref_json

        # The regex substitution
        repl = re.subn(r'<extref\s+type=\\"simple\\"\s+href=',r'<extref xlink:type=\"simple\" xlink:href=', ref_json, flags=re.DOTALL)

        if repl[1] > 0: # [1] is the count of replacements from subn
            # there is a change
            # Save copy of existing object
            print('Saving data to ' + out_path + '....')

            with open(out_path, "w+") as f:
                f.write(data_old)

            data_new = repl[0]
            cnt +=1
            print('Posting ' + str(repo) + '_' + str(asid) + ' to ' + server)
            z = asf.postArchivalObject(repo,asid,data_new)
            print(z)
            print(' ')


    print('Total replacements: ' + str(cnt))




if __name__ == '__main__':
    main()
