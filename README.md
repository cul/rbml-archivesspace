# rbml-archivesspace

This repository contains scripts for migrating and manipulating ArchivesSpace data in the Columbia University Libraries context.

All scripts that call the API require a secrets.py file, formatted as follows:

~~~~
baseURL='https://{API_endpoint}'
user='{username}'
password='{password}'
~~~~