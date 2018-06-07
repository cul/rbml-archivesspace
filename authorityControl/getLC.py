import requests, csv, json, urllib, time
from fuzzywuzzy import fuzz

startTime = time.time()

#this will call back LC numbers from a list of names, and output the name, lc number, AS number, and if the match isn't unique, flag it
#one could run this in conjunction with the viaf one, to try to confirm matches and weed out some of the flagged ones

baseURLexact = 'http://id.loc.gov/authorities/names/label/'
baseURL = 'http://id.loc.gov/search/?q='
with open('input_agent.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            name = str(row[0])
            rowEdited = urllib.quote(name.strip())
            #test for exact match
            url = baseURLexact+rowEdited
            response = requests.get(url)
            if response.history:
                for resp in response.history:
                    if str(resp.status_code) == '303':
                        print name, '|', resp.url.split("/names/",1)[1], '|' , row[1]
            #if no exact match, send the string with an ending wildcard 
            else:
                url2 = baseURL+'"'+rowEdited+'*'+'"'
                response2 = requests.get(url2).content
                #check for more than one match in response2 using a test of some sort
                if '<td>2.' in response2:
                    print name, '|', response2.split("/authorities/names/",1)[1].split('"',1)[0], '|' , row[1], '|', 'FLAGGED_MULTIPLE' 
                else:
                    #otherwise just give back the auth no of the match
                    print name, '|', response2.split("/authorities/names/",1)[1].split('"',1)[0], '|' , row[1]
            #add a one second pause for each
            time.sleep(1) 

                   
# show script runtime
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)