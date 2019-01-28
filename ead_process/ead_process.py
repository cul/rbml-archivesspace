import GoogleSheetAPITools as gs
import subprocess
import re
from lxml import etree as et
import secrets

# Script to read EAD XML from two different sources and put them 
# in a Google Sheet for comparison and analysis.
# A set of Xpaths is defined for each data source, with the keys
# becoming heads in the spreadsheet.
#
# Each set requires a file list text file with paths (relative to
# defined source folder) for all files to be processed.



def main():

    # Default namespace for CUL EADs
    ns = {"ead": "urn:isbn:1-931666-22-9"}


    data_folder1 = '/Users/dwh2128/Documents/ACFA/exist-local/backups/for_migration/ead-export-20190123'
    data_folder2 = 'ead_process/xml'

    file_list1 = 'ead_process/file_paths.txt'
    file_list2 = 'ead_process/as_filepaths.txt'
    # file_list1 = 'ead_process/file_path_TEST.txt'
    # file_list2 = 'ead_process/as_file_path_TEST.txt'



    the_sheet = secrets.default_sheet # Google sheet id in "secrets"
#    the_sheet = '1Daww5TrXK8pCzEneFwx4UzaGqJr_buODztE61BPRxHA'

    range1 = 'ead-legacy!A:Z' # tab for legacy EAD data
    range2 = 'ead-as!A:Z' # tab for AS exported EAD data


    # Dict of elements and their xpath. These are used for legacy EADS.
    legacyQs = { 
        "bibid": "ead:archdesc/ead:did/ead:unitid[@type='clio'][1]/text()",
        "repo": "ead:archdesc/ead:did/ead:unitid[1]/@repositorycode",
        "title": "ead:archdesc/ead:did/ead:unittitle[1]/text()",
        "status" : "ead:eadheader/@findaidstatus", 
        "revisiondesc": "ead:eadheader/ead:revisiondesc",
        "altformavail": "ead:archdesc/ead:altformavail",
        "accruals": "ead:archdesc/ead:accruals",
        "accessrestrict": "ead:archdesc/ead:accessrestrict", 
        "userestrict": "ead:archdesc/ead:userestrict",
        "acqinfo": "ead:archdesc/ead:acqinfo",
        "arrangement": "ead:archdesc/ead:arrangement",
        "bibliography": "ead:archdesc/ead:bibliography",
        "bioghist": "ead:archdesc/ead:bioghist",
        "scopecontent": "ead:archdesc/ead:scopecontent",
        "controlaccess": "ead:archdesc/ead:controlaccess",
        "custodhist": "ead:archdesc/ead:custodhist",
        "separatedmaterial": "ead:archdesc/ead:separatedmaterial",
        "otherfindaid": "ead:archdesc/ead:otherfindaid",
        "relatedmaterial": "ead:archdesc/ead:relatedmaterial",
        "abstract": "ead:archdesc/ead:did/ead:abstract",
        "physloc": "ead:archdesc/ead:did/ead:physloc",
        "processinfo": "ead:archdesc/ead:processinfo",
        "unitid": "ead:archdesc/ead:did/ead:unitid",
        "prefercite": "ead:archdesc/ead:prefercite"

    }

    # Dict of elements and their xpath. These are used for AS EADS. (Slightly different Xpath for some elements.)
    asQs = { 
        "bibid": "ead:archdesc/ead:did/ead:unitid[1]/text()",
        "repo": "ead:eadheader/ead:eadid[1]/@mainagencycode",
        "title": "ead:archdesc/ead:did/ead:unittitle[1]/text()",
        "status" : "ead:eadheader/@findaidstatus", 
        "revisiondesc": "ead:eadheader/ead:revisiondesc",
        "altformavail": "ead:archdesc/ead:altformavail",
        "accruals": "ead:archdesc/ead:accruals",
        "accessrestrict": "ead:archdesc/ead:accessrestrict", 
        "userestrict": "ead:archdesc/ead:userestrict",
        "acqinfo": "ead:archdesc/ead:acqinfo",
        "arrangement": "ead:archdesc/ead:arrangement",
        "bibliography": "ead:archdesc/ead:bibliography",
        "bioghist": "ead:archdesc/ead:bioghist",
        "scopecontent": "ead:archdesc/ead:scopecontent",
        "controlaccess": "ead:archdesc/ead:controlaccess",
         "custodhist": "ead:archdesc/ead:custodhist",
        "separatedmaterial": "ead:archdesc/ead:separatedmaterial",
        "otherfindaid": "ead:archdesc/ead:otherfindaid",
        "relatedmaterial": "ead:archdesc/ead:relatedmaterial",
        "abstract": "ead:archdesc/ead:did/ead:abstract",
        "physloc": "ead:archdesc/ead:did/ead:physloc",
        "processinfo": "ead:archdesc/ead:processinfo",
        "unitid": "ead:archdesc/ead:did/ead:unitid",
        "prefercite": "ead:archdesc/ead:prefercite"

    }

    data_data = [[data_folder1,file_list1,range1,legacyQs],[data_folder2,file_list2,range2,asQs]]

    for d in data_data:
        the_folder = d[0]
        the_data = d[1]
        the_target = d[2]
        theQs = d[3]
        

        # this will be the result dict.
        theElements = { }

        # Initialize data set and populate first row with headers (dict keys).
        theHeads = list(theQs.keys())
        theXpaths = list(theQs.values())
        theData = [theHeads,theXpaths]

        # initialize sheet
        c = gs.sheetClear(the_sheet,the_target)

        with open(the_data) as f: 
            file_list = [line.rstrip('\n') for line in f]


        
        for a_file in file_list:

            the_path = str(the_folder + '/' + a_file)

            
            print('Processing file: ' + the_path)

            try:
                tree = et.parse(the_path)
                root = tree.getroot()
                
                for q in theQs:
                    # Query the XML using xpath expression.
                    x = root.xpath(theQs[q], namespaces=ns)

                    try:
                        # is a subtree

                        if len(x) > 1:
                            # test for case where more than one node matches xpath.
                            theValues = []
                            for i in x:
                                aValue = str(et.tostring(i).decode('utf-8'))
                                theValues.append(aValue)
                            theValue = '<BR/> '.join(theValues)
                            theValue = text_clean(theValue)

                        else:
                            theValue = str(et.tostring(x[0]).decode('utf-8'))
                            theValue = text_clean(theValue)
                    
                    except:
                        try:
                            # is an attribute or text node
                            theValue = str(x[0])
                            theValue = text_clean(theValue)
                        except:
                            theValue = ""

                    #TODO: make sure this covers all expected types of output.


                    theElements[q] = theValue

                theRow=list(theElements.values())

                #print(theRow)

                theData.append(theRow)
            
            except:
                print('*** Could not process ' + the_path + ' ***')

        # Write data to Google Sheet.

        print('Writing data to Google Sheet ...')
        gs.sheetAppend(the_sheet,the_target,theData)

    print('Done.')



    quit()






def text_clean(the_str):
    the_str = " ".join(re.split("\s+", the_str, flags=re.UNICODE))
    the_str = re.sub('\s?xmlns=".*?"', '', the_str)
    the_str = re.sub('\s?xmlns:\w+=".*?"', '', the_str)
    the_str = re.sub(r'(<subject)', r'\n\1', the_str)
    the_str = re.sub(r'(<persname)',  r'\n\1', the_str)
    the_str = re.sub(r'(<corpname)',  r'\n\1', the_str)
    the_str = re.sub(r'(<p)', r'\n\1', the_str)
    the_str = re.sub(r'<head>.*?</head>', r'', the_str)
    the_str = re.sub(r'\n\n',  r'\n', the_str)
    the_str = re.sub('<BR/>', '\n\n', the_str)
    return the_str

if __name__ == '__main__':
    main()



