# rbml-archivesspace/APIFunctions

These scripts interact with the ArchivesSpace API. Current development is focussed on ASFunctions.py, which is intended to be imported as a function library in other scripts. It is currently in Python 3, while the individual action scripts are still in Python 2.

Scripts in the repo require a secrets.py (prod) or secretsDev.py (dev) file, formatted as follows:

~~~~
baseURL='https://{API_endpoint}'
user='{username}'
password='{password}'
baseOAIURL='{OAI URL, eg., https://aspace.library.columbia.edu/public/oai}'
oaiPrefix = '{OAI prefix, e.g., oai:columbia}'
~~~~

