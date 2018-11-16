from lp_backup import Runner

# create backup runner
example_backup_runner = Runner("/home/YOUR_USER/.config/lp_backup.yml")
# run backup
backup_file_name = example_backup_runner.backup()
print(backup_file_name)

# restore backup to /tmp/example-full-restore.csv (which is PLAIN TEXT, be sure to delete after use)
backup_file_name.restore(backup_file_name, "/tmp/test-full-restore.csv")
