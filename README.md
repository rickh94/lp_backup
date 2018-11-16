# Lastpass Backup
[![Build Status](https://travis-ci.org/rickh94/lp_backup.svg?branch=master)](https://travis-ci.org/rickh94/lp_backup)

Easily backup data from lastpass to your own storage.

## Installation

You first need to install the [lastpass commandline
tool](https://github.com/lastpass/lastpass-cli) for your platform.
It is used internally for accessing the lastpass api.

Then clone the repo and run `python3 setup.py install`

Install [fs.webdavfs](https://github.com/PyFilesystem/webdavfs) for webdav support.

## Usage

```python
from lp_backup import Runner

# create backup runner 
example_backup_runner = Runner("/home/YOUR_USER/.config/lp_backup.yml")
# run backup
backup_file_name = example_backup_runner.backup()
print(backup_file_name)

# restore backup to /tmp/example-full-restore.csv (which is PLAIN TEXT, be sure to delete after use)
backup_file_name.restore(backup_file_name, "/tmp/test-full-restore.csv")

```


