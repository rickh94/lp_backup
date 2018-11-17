from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))
VERS = '0.1'
DESC = 'Script to create local backups from Lastpass'

with open(path.join(HERE, 'README.md'), 'r') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='lp_backup',
    version=VERS,

    description=DESC,
    long_description=LONG_DESCRIPTION,

    url='https://github.com/rickh94/lp_backup',
    author='Rick Henry',
    author_email='fredericmhenry@gmail.com',

    license='MIT',
    python_requires='>=3.6',

    packages=find_packages(),

    install_requires=[
        # 'sultan',
        'boto3',
        'fs==2.1.2',
        'fs-s3fs',
        'ruamel.yaml',
        'cryptography',
        'fs.webdavfs'
    ],
    tests_require=['pytest', 'pytest-cov', 'freezegun'],
    # setup_requires=['pytest-runner'],
    dependency_links=[
        "http://github.com/damndam/webdavfs/tarball/master#egg=fs.webdavfs"
    ]

)
