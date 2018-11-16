# Usage


## Creating Backups

Create a simple python script, for instance `backup.py` with the contents:

```python
  from lp_backup import Runner

  run = Runner(path='/path/to/config/file.yaml')
  backup_file_name = run.backup()
```


## Restoring from Backups

This will create a plain text csv file that you can import into lastpass or another
password manager.

```python
from lp_backup import Runner
run = Runner(path='/path/to/config/file.yml')
run.restore(backup_file_name, output_file_name)
```

It is crucial that you use the exact configuration file used to create the initial
backup or your data might be garbled.

