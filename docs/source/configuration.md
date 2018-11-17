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
The configuration file is in YAML syntax. If you are unfamiliar,
[this seems helpful](https://github.com/Animosity/CraftIRC/wiki/Complete-idiot's-introduction-to-yaml).
There are several configuration options available:

* ``Email:`` *Required* The email address for your lastpass account
* ``Trust:`` Whether to trust this computer after the backup in the lastpass cli
* ``Encryption Key:`` This can be set to ``null`` or ``generate`` for your first run. It is highly recommended
that it be left set to ``generate``. On first run, an encryption key will be generated and saved into the configuration
file (don't lose it). This file should be kept safe.
* ``Compression:`` Whether to compress the data. If ``true``, the data will be lzma compressed and saved with
a ``.xz`` extension.
* ``Date``: Whether to include the date in filenames.
* ``Prefix``: Path prefix (folders) to put the backup file in.
* ``Backing Store:`` List of locations to put backups. Specify a uri as documented at
 [pyfilesystem2](http://pyfilesystem2.readthedocs.io/en/latest/builtin.html) for osfs,
 mountfs, ftpfs. You can use non-native filesystems (e.g. sshfs) but you will
 need to install the corresponding extensions to pyfilesystem2. Obviously this
 must be accessible to the backup program when it runs.
 You may also specify S3 for Amazon Simple Storage Service or s3 compatible service, as well as a WebDav server.
  * Mixed Example:
  ```yaml
  Backing Store:
  - URI: /home/YOURUSER/lastpass_backups
  - Type: S3
    Bucket: lastpass_backup_bucket
  - Type: webdav
    Base URL: https://example.com
    Root: /remote.php/webdav
    Username: YOURUSER
    Password: $WEBDAV_PASSWORD
    ```
  * ``S3``:  It is recommended that you use external authentication for S3 (env vars or
IAM roles), but you may specify Key ID and Secret Key, preferably through env vars.
Be sure to specify Endpoint URL and ensure authentication for S3 compatible services
Specify Date: True for adding date information to the backup file/folders.
    * Example S3 configuration:
    ```yaml
    Backing Store:
      - Type: S3
        Bucket: mybackupbucket
    ```
    * Example S3 compatible service (digital ocean spaces):
    ```yaml
    Backing Store:
      - Type: S3
        Bucket: mybackupbucket
        Endpoint URL: https://nyc3.digitaloceanspaces.com
        Key ID: $DOKEY
        Secret Key: $DOSECRET
     ```
   * `webdav`: You can use any webdav service with password authentication.
   You can store the relevant information in the config file, or specify
   environment variables
   The webdav library in use separates the base part of the url from the
   root of the webdav server, so split your url accordingly.

     Example Configuration:
     ```yaml
     Backing Store:
      - Type: webdav
        Base URL: https://mynextcloudserver.com
        Root: /remote.php/webdav
        Username: john
        Password: my-single-app-password
     ```

     *IF YOU DO THIS: please please please don't use your main password, set up multi-factor authentication
     and generate a single app password. This is a plain text file protected only by filesystem permissions
     (which should probably be 600, by the way). Even better, make a dedicated user account for this purpose,
     so that none of your other data is put at risk.*
