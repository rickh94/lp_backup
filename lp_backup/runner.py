import datetime
import os
import lzma
import subprocess

# from sultan.api import Sultan
from ruamel.yaml import YAML
from cryptography.fernet import Fernet
import fs
# from fs import tempfs
# from fs import tarfs
# from fs import zipfs
from fs.errors import CreateFailed
from fs_s3fs import S3FS
# import sultan

from lp_backup import file_io
from lp_backup import exceptions
# from . import __docurl__


class Runner(object):
    """
    This class handles orchestration of downloading and storing the backup.
    Options are set in a yaml configuration file. There is an
    :download:`example <./sample-config.yaml>` you can use as a
    starting point.

    :param path: (required) absolute path to the file on the system or relative to
        the FS object supplied in the filesystem parameter
    :param filesystem: (keyword only) a pyfilesystem2 FS object where the yaml config
        file is located.
    """
    def __init__(self, path, *, filesystem=None):
        self.yaml = YAML()
        self.config_path = str(path)
        if not filesystem:
            self.filesystem = fs.open_fs('/')
        else:
            self.filesystem = filesystem
        with self.filesystem.open(self.config_path, 'r') as configfile:
            self.config = self.yaml.load(configfile)
        # self.sultan = Sultan()
        self.logged_in = False
        self.configure_encryption()

    def login(self):
        trust = ""
        if self.config['Trust']:
            trust = "--trust"
        out = subprocess.run(["lpass", "login", self.config["Email"], trust], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if out.stderr:
            print(out.stderr)
            raise exceptions.LoginFailed(out.stderr)
        if "Success:" in out.stdout[0]:
            self.logged_in = True
        else:
            print(out.stderr + " " + out.stdout)
            raise exceptions.LoginFailed(out.stderr + " " + out.stdout)

    def configure_encryption(self):
        if self.config["Encryption Key"] is None:
            self.fernet = None
            return
        if self.config["Encryption Key"].lower() == "generate":
            new_key = Fernet.generate_key()
            self.config["Encryption Key"] = new_key
            with self.filesystem.open(self.config_path, 'w') as config_file:
                self.yaml.dump(self.config, config_file)
        try:
            self.fernet = Fernet(self.config["Encryption Key"])
        except ValueError as err:
            raise exceptions.InvalidKey("Could not find valid encryption key: "
                    + err)

    def backup(self):
        """
        Using the configuration from the file, create the backup.
        """
        if not self.logged_in:
            self.login()
        # print("logged in")
        # sync = self.sultan.lpass("sync").run()
        # if sync.stderr:
        #     raise exceptions.BackupFailed(sync.stderr)
        # print("synced")
        # run_backup = self.sultan.lpass("export").run()
        run_backup = subprocess.run(["lpass", "export"], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        file_suffix = '.csv'
        if run_backup.stderr:
            raise exceptions.BackupFailed(run_backup.stderr)
        # print("backup downloaded")
        backup_lines = run_backup.stdout
        backup_data = '\n'.join(backup_lines)
        if self.fernet:
            backup_data = self.fernet.encrypt(backup_data.encode('utf-8'))
            file_suffix += ".encrypted"
        if self.config.get("Compression", False):
            backup_data = lzma.compress(backup_data)
            file_suffix += ".xz"
        # with open("/tmp/testbackup.csv.encrypted.xz", 'wb') as test_file:
        #     test_file.write(backup_data)
        try:
            outfs = self._configure_backing_store()
            prefix = self.config['Backing Store'].get('Prefix', '')
            if self.config['Backing Store'].get('Date', False):
                date = datetime.datetime.today().isoformat() + "-"
            else:
                date = ""
        except KeyError as err:
            _config_error(err)
        outfile = (date + self.config["Email"] +
                "-lastpass-backup" + file_suffix)
        file_io.write_out_backup(
            backing_store_fs=outfs,
            outfile=outfile,
            prefix=prefix,
            data=backup_data
        )
        return outfile

    def restore(self, infilename, new_file):
        try:
            restorefs = self._configure_backing_store()
            prefix = self.config["Backing Store"].get("Prefix", "")
        except KeyError as err:
            _config_error(err)
        restored_data = file_io.read_backup(restorefs, infilename, prefix)
        if self.config.get("Compression", False):
            restored_data = lzma.decompress(restored_data)
        if self.fernet:
            restored_data = self.fernet.decrypt(restored_data)
        with self.filesystem.open(str(new_file), 'w') as the_new_file:
            the_new_file.write(restored_data.decode('utf-8'))

    def _configure_backing_store(self):
        try:
            bs = self.config['Backing Store']
            if 'Type' in bs:
                for key, item in bs.items():
                    bs[key] = _get_from_env(item)
                if bs['Type'].lower() == 's3':
                    return S3FS(
                        bs['Bucket'],
                        strict=False,
                        aws_access_key_id=bs.get('Key ID', None),
                        aws_secret_access_key=bs.get('Secret Key', None),
                        endpoint_url=bs.get('Endpoint URL', None)
                    )
            else:
                return fs.open_fs(bs['URI'], create=True)
        except (KeyError, OSError, CreateFailed) as err:
            _config_error(err)


def _config_error(err=''):
    raise exceptions.ConfigurationError(
        "Options are missing in the configuration file. "
        f"Please consult the docs at {__docurl__}.\n"
        f"{err}")


def _get_from_env(item):
    if item is None:
        return None
    try:
        if item[0] == '$':
            return os.environ[item[1:]]
    except TypeError:
        pass
    return item
