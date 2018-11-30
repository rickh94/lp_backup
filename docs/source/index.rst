.. Lastpass Backup documentation master file, created by
   sphinx-quickstart on Fri Nov 16 15:56:40 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Lastpass Backup
===============

Installation
------------

You first need to install the `lastpass commandline
tool <https://github.com/lastpass/lastpass-cli>`_ for your platform.
It is used internally for accessing the lastpass api.

```$ pip install lp_backup```


Usage
-----

.. code-block:: python

    from lp_backup import Runner

    # create backup runner
    example_backup_runner = Runner("/home/YOUR_USER/.config/lp_backup.yml")
    # run backup
    backup_file_name = example_backup_runner.backup()
    print(backup_file_name)

    # restore backup to /tmp/example-full-restore.csv (which is PLAIN TEXT, be sure to delete after use)
    backup_file_name.restore(backup_file_name, "/tmp/test-full-restore.csv")



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   configuration
   usage
   apidoc



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
