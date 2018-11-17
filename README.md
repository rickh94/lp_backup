# Lastpass Backup
[![Build Status](https://travis-ci.org/rickh94/lp_backup.svg?branch=master)](https://travis-ci.org/rickh94/lp_backup)
[![Documentation Status](https://readthedocs.org/projects/lastpass-local-backup/badge/?version=latest)](https://lastpass-local-backup.readthedocs.io/en/latest/?badge=latest)

Easily backup data from lastpass to your own storage.

## Installation

You first need to install the [lastpass commandline
tool](https://github.com/lastpass/lastpass-cli) for your platform.
It is used internally for accessing the lastpass api.

```bash
$ pip install lp_backup
```

Install [fs.webdavfs](https://github.com/damndam/webdavfs) for webdav support.

## Usage

```
from lp_backup import Runner

# create backup runner
example_backup_runner = Runner("/home/YOUR_USER/.config/lp_backup.yml")
# run backup
backup_file_name = example_backup_runner.backup()
print(backup_file_name)

# restore backup to /tmp/example-full-restore.csv (which is PLAIN TEXT, be sure to delete after use)
backup_file_name.restore(backup_file_name, "/tmp/test-full-restore.csv")

```


