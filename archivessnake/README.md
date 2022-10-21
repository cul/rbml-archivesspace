# archivessnake

These scripts use ArchivesSnake to export data from and push data to ArchivesSpace.

## Requirements

* See requirements.txt

## Installation

These scripts require a local configurations file, which should be created in the same directory as the script and named `local_settings.cfg`. A sample file looks like this:

```
    [ArchivesSpace]
    # the base URL of your ArchivesSpace installation
    baseURL:http://localhost:8089
    username:admin
    password:admin
```


