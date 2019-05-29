#nb: python3

import csv

#open a csv in the form term, uri, number of subdivisions
reader = csv.reader(open('as_TEST_subjects.csv', 'r'))

#read the csv into a master list
masterList=[]
for row in reader:
    masterList.append(row)

#function that searches master list for a term, and returns victim uri (the one with only 1 subdivision)
def searchMasterList (searchString):
    for LIST in masterList:
        if (searchString == LIST[0] and int(LIST[2]) == 1):
            return LIST[1]

#loop that looks for terms with more than one subdivision (the targets); prints the target uri; calls function to call back victim uri
for LIST in masterList:
    if (int(LIST[2]) > 1 and searchMasterList(LIST[0])):
        print LIST[0], "|", LIST[1], "|", searchMasterList(LIST[0])
