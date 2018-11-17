import datetime
import os
import lzma
import subprocess

from ruamel.yaml import YAML
from cryptography.fernet import Fernet
import fs
from fs.errors import CreateFailed
from fs_s3fs import S3FS

webdav_available = False
try:
    from webdavfs.webdavfs import WebDAVFS
    webdav_available = True
except ModuleNotFoundError:
    webdav_available = False



from lp_backup import file_io
from lp_backup import exceptions
# from lp_backup import __docurl__


class Runner(object):
    """
    This class handles orchestration of downloading and storing the backup.
    Options are set in a yaml configuration file. There is an
    :download:`example <https://github.com/rickh94/lp_backup/blob/master/docs/source/sample-config.yml>`
    you can use as a starting point.

    :param path: absolute path to the file on the system or relative to
        the FS object supplied in the filesystem parameter
    :param keyword filesystem: a pyfilesystem2 FS object where the yaml config
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
        outfs = None
        prefix = None
        try:
            outfs = self._configure_backing_store()
            prefix = self.config.get('Prefix', '')
            if self.config.get('Date', False):
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
        """
        Restore backup to a plain text csv file for uploading to password manager.

        :param infilename:  the name of the backup file
        :param new_file: the filename to save the data to

        """
        try:
            restorefs = self._configure_backing_store()
            prefix = self.config.get("Prefix", "")
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
            backing_stores = []
            for bs in self.config['Backing Store']:
                if 'Type' in bs:
                    for key, item in bs.items():
                        bs[key] = _get_from_env(item)
                    if bs['Type'].lower() == 's3':
                        backing_stores.append(S3FS(
                            bs['Bucket'],
                            strict=False,
                            aws_access_key_id=bs.get('Key ID', None),
                            aws_secret_access_key=bs.get('Secret Key', None),
                            endpoint_url=bs.get('Endpoint URL', None)
                        ))
                    elif 'dav' in bs['Type'].lower():
                        if not webdav_available:
                            raise exceptions.NoWebdav("no webdavfs module was found")
                        if bs['Root'][0] != '/':
                            bs['Root'] = '/' + bs['Root']
                        backing_stores.append(WebDAVFS(
                            url=bs['Base URL'],
                            login=bs['Username'],
                            password=bs['Password'],
                            root=bs['Root']
                        ))
                    else:
                        _config_error("Unknown filesystem type.")
                else:
                    backing_stores.append(fs.open_fs(bs['URI'], create=True))
        except (KeyError, OSError, CreateFailed) as err:
            _config_error(err)
        return backing_stores


def _config_error(err=''):
    raise exceptions.ConfigurationError(
        "Options are missing in the configuration file. "
        f"Pleaseconsult the docs at https://lastpass-local-backup.readthedocs.io\n"
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
