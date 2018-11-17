import botocore
import fs
from fs.copy import copy_file
from fs.errors import DirectoryExists
from fs import tempfs

from lp_backup import exceptions


def write_out_backup(backing_store_fs, data, outfile, prefix=''):
    """
    Write the backup data to its final location. A backing store is required
    and either a filepath to the packaged backup or the tmp filesystem is required.

    :param backing_store_fs: a pyfilesystem2 object to be the final storage
            location of the backup. (should be `OSFS`, `S3FS`, `FTPFS`, etc.)
            Can be a single object or list of filesystem objects for copying to
            multiple backing stores.
    :param data: the byte stream that needs to be written to the file
        on the backing store fs.
    :param outfile: the name of the file to write out to.
    :param optional prefix: a parent directory for the files to be saved under.
            This is can be a good place to encode some information about the
            backup. A slash will be appended to the prefix to create
            a directory or pseudo-directory structure.

    """
    if prefix and not prefix[-1] == '/':
        prefix = prefix + '/'
    if not isinstance(backing_store_fs, list):
        backing_store_fs = [backing_store_fs]
    for backing_fs in backing_store_fs:
        # print(backing_fs)
        tmp = tempfs.TempFS()
        with tmp.open("lp-tmp-backup", 'wb') as tmp_file:
            tmp_file.write(data)
        try:
            backing_fs.makedirs(prefix)
        except DirectoryExists:
            pass
        # print(prefix, outfile)
        copy_file(tmp, "lp-tmp-backup", backing_fs, str(prefix + outfile))
        tmp.clean()


def read_backup(backing_store_fs, infile, prefix=""):
    """
    Read a backup file from some pyfilesystem.

    :param backing_store_fs: The pyfilesystem object where the file is located
    :param infile: the name of the file
    :param optional prefix: the prefix before the filename

    :return: raw file data
    """
    tmp = tempfs.TempFS()
    # data = ""
    if prefix and not prefix[-1] == '/':
        prefix = prefix + '/'
    if not isinstance(backing_store_fs, list):
        backing_store_fs = [backing_store_fs]
    restore_succeeded = False
    for backing_fs in backing_store_fs:
        try:
            copy_file(backing_fs, prefix + infile, tmp, infile)
            restore_succeeded = True
            break
        except (botocore.exceptions.NoCredentialsError, OSError,
                fs.errors.ResourceNotFound, fs.errors.PermissionDenied):
            continue
    if not restore_succeeded:
        raise exceptions.ConfigurationError("Specified file could not be found in any"
                                            " of the available backing stores.")
    with tmp.open(infile, 'rb') as retrieved_file:
        data = retrieved_file.read()
    tmp.clean()
    return data
