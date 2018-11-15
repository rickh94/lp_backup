from lp_backup import Runner

test = Runner("/home/rick/repositories/lp_backup/testconfig.yaml")
backup_file_name = test.backup()
test.restore(backup_file_name, "/tmp/test-full-restore.csv")
