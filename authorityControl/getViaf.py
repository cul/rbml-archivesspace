import requests, csv, json, urllib, time
from fuzzywuzzy import fuzz

startTime = time.time()

baseURL = 'http://viaf.org/viaf/search/viaf?query=local.personalNames+%3D+%22'
with open('input_agent.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            name = str(row[0])
            rowEdited = urllib.quote(name.strip())
            url = baseURL+rowEdited+'%22+and+local.sources+%3D+%22lc%22&sortKeys=holdingscount&maximumRecords=1&httpAccept=application/rdf+json'
            response = requests.get(url).content
            try:
                response = response[response.index('<recordData xsi:type="ns1:stringOrXmlFragment">')+47:response.index('</recordData>')].replace('&quot;','"')
                response = json.loads(response)
                label = response['mainHeadings']['data'][0]['text']
                viafid = response['viafID']
                #grab lc number
                lcdict = response['sources']['source']
                for k in lcdict:
                    if k['#text'].startswith('LC'):
                        lcno = k['@nsid']
            except:
                label = ''
                viafid = ''
            ratio = fuzz.ratio(row, label)
            partialRatio = fuzz.partial_ratio(row, label)
            tokenSort = fuzz.token_sort_ratio(row, label)
            tokenSet = fuzz.token_set_ratio(row, label)
            avg = (ratio+partialRatio+tokenSort+tokenSet)/4
            print name.strip(), '|' , row[1], '|' , row[2], '|' , label, '|' , viafid, '|' , lcno, '|' , ratio, '|' , partialRatio, '|' , tokenSort, '|' , tokenSet, '|' , avg
            #add a one second pause for each
            time.sleep(1)        
# show script runtime
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)