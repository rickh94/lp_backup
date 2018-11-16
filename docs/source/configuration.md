# Configuration


## Getting Started


A great starting point is the [example configuration
    file](https://github.com/rickh94/lp_backup/blob/master/docs/source/sample-config.yml).


## What You'll Need
 * Your lastpass username (email) and password.
 * The [lastpass command line tool](https://github.com/lastpass/lastpass-cli).
 * Somewhere to put the backups. This can be a local directory, S3 or S3
   compatible service, or [any builtin in filesystem of
   pyfilesystem2](https://docs.pyfilesystem.org/en/latest/builtin.html). If
   pyfilesystem2 has an extension for the filesystem you want to use, it
   should work but you will need to install the extension separately.

## Configuration File
There are several configuration options available:

* ``Email:`` *Required* The email address for your lastpass account
* ``Trust:`` Whether to trust this computer after the backup in the lastpass cli
* ``Encryption Key:`` This can be set to ``null`` or ``generate`` for your first run. It is highly recommended
that it be left set to ``generate``. On first run, an encryption key will be generated and saved into the configuration
file (don't lose it). This file should be kept safe.
* ``Compression:`` Whether to compress the data. If ``true``, the data will be lzma compressed and saved with
a ``.xz`` extension.
* ``Backing Store:`` Where to put the final backup. Specify a uri as documented at
 [pyfilesystem2](http://pyfilesystem2.readthedocs.io/en/latest/builtin.html) for osfs,
 mountfs, ftpfs. You can use non-native filesystems (e.g. sshfs) but you will
 need to install the corresponding extensions to pyfilesystem2. Obviously this
 must be accessible to the backup program when it runs.
 Backing Store:
   URI: /home/backupuser/backups
 You may also specify S3 for Amazon Simple Storage Service or s3 compatible service, as well as a webdav server.
  * ``S3``:  It is recommended that you use external authentication for S3 (env vars or
IAM roles), but you may specify Key ID and Secret Key, preferably through env vars.
Be sure to specify Endpoint URL and ensure authentication for S3 compatible services
Specify Date: True for adding date information to the backup file/folders.
    * Example S3 configuration:
    ```yaml
    Backing Store:
      Type: S3
      Bucket: mybackupbucket
      Prefix: backupfolder/
      Date: True
    ```
    * Example S3 compatible service (digital ocean spaces):
    ```yaml
    Backing Store:
      Type: S3
      Bucket: mybackupbucket
      Endpoint URL: https://nyc3.digitaloceanspaces.com
      Key ID: $DOKEY
      Secret Key: $DOSECRET
     ```
   * Example Webdav:
     *IF YOU DO THIS: please please please don't use your main password, set up multi-factor authentication
     and generate a single app password. This is a plain text file protected only by filesystem permissions
     (which should probably be 600, by the way). Even better, make a dedicated user account for this purpose,
     so that none of your other data is put at risk.*
     ```yaml
     Backing Store:
      Type: webdav
      URL: https://mynextcloudserver.com/remote.php/webdav
      Username: john
      Password: my-single-app-password
      Prefix: my/lastpass/backups
      Date: True
     ```
