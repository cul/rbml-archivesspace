# rbml-archivesspace

This repository contains scripts for migrating and manipulating ArchivesSpace data in the Columbia University Libraries context.

All scripts that call the API require a secrets.py (prod) or secretsDev.py (dev) file, formatted as follows:

~~~~
baseURL='https://{API_endpoint}'
user='{username}'
password='{password}'
baseOAIURL='{OAI URL, eg., https://aspace.library.columbia.edu/public/oai}'
oaiPrefix = '{OAI prefix, e.g., oai:columbia}'
~~~~


These scripts are inspired by and indebted by many existing ASpace code repos, but in particular to Lora Woodford's API workshop (https://github.com/lorawoodford/api-training).
