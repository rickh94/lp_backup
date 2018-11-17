# Installation

You must install the [lastpass cli](https://github.com/lastpass/lastpass-cli) and have it available in your path.


You will need Python 3.6 or later installed, as well as pip.

```bash
$ pip install lp_backup
```

You may want to do it in a virtual environment.

## Webdav support

There is a bug in the webdavfs library preventing it from installing properly.
For webdav support you can install it from a fork with
```bash
$ pip install git+https://github.com/damndam/webdavfs
```

or if you use ``pipenv``, download my [Pipfile](https://github.com/rickh94/lp_backup/blob/master/Pipfile)
 and use that for the dependencies.