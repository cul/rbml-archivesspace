import GoogleSheetAPITools as gs
import subprocess
import re
import os
from lxml import etree as et

# Script to read EAD XML and report specified element data to a Google sheet.




def main():

    data_folder = '/path/to/files'
    the_sheet = 'replace-with-google-sheet-id'
    the_range = 'replace-with-name-of-tab!A:Z' 

    the_file_paths = []

    for root, dirs, files in os.walk(os.path.abspath(data_folder)):
        for file in files:
            the_file_paths.append(os.path.join(root, file))


    # print(the_file_paths)

    the_queries = { 
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


    # do it
    ead_report(the_sheet,the_range,the_file_paths,the_queries)


    quit()


def ead_report(the_sheet,the_range,the_files,the_qs):

    # Default namespace for CUL EADs
    ns = {"ead": "urn:isbn:1-931666-22-9"}

    the_heads = list(the_qs.keys())
    the_xpaths = list(the_qs.values())
    the_data = [the_heads,the_xpaths]


    gs.sheetClear(the_sheet,the_range)

    # this will be the result dict.
    theElements = { }

    for a_file in the_files:
        
        print('Processing file: ' + a_file)

        try: 
                
            tree = et.parse(a_file)
            root = tree.getroot()
            
            for q in the_qs:
                # Query the XML using xpath expression.
                x = root.xpath(the_qs[q], namespaces=ns)

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

            print(theRow)

            the_data.append(theRow)

        except:
            print('*** Could not process ' + a_file + ' ***')


    # Write data to Google Sheet.

    print('Writing data to Google Sheet ...')
    gs.sheetAppend(the_sheet,the_range,the_data)



    # add stuff here
    print('Done.')
   


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



