from runner import Runner

test = Runner("/home/rick/repositories/lp-backup/testconfig.yaml")
backup_file_name = test.backup()
test.restore(backup_file_name, "/tmp/test-full-restore.csv")
