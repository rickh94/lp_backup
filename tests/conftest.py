import pytest
import os
import shutil
from unittest import mock
from pathlib import Path
from ruamel.yaml import YAML
from lp_backup.runner import Runner

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


@pytest.fixture
def tmp_config_file_one(tmpdir):
    test_config_file = Path(DATA, "testconfig.yml")
    shutil.copy2(test_config_file, tmpdir)
    temp_config_file = Path(tmpdir, "testconfig.yml")
    return temp_config_file


@pytest.fixture
def tmp_config_file_two(tmpdir):
    test_config_file = Path(DATA, "testconfig-2.yml")
    shutil.copy2(test_config_file, tmpdir)
    temp_config_file = Path(tmpdir, "testconfig-2.yml")
    return temp_config_file


@pytest.fixture
def tmp_config_file_three(tmpdir):
    test_config_file = Path(DATA, "testconfig-4.yml")
    shutil.copy2(test_config_file, tmpdir)
    temp_config_file = Path(tmpdir, "testconfig-4.yml")
    return temp_config_file


@pytest.fixture
def test_runner_one(tmp_config_file_one, monkeypatch, mocker):
    new_runner = Runner(tmp_config_file_one)
    monkeypatch.setattr(new_runner, 'logged_in', True)
    return new_runner


@pytest.fixture
def test_runner_two(tmp_config_file_two, monkeypatch):
    new_runner = Runner(tmp_config_file_two)
    monkeypatch.setattr(new_runner, 'logged_in', True)
    return new_runner


@pytest.fixture
def test_runner_three(tmp_config_file_three, monkeypatch):
    new_runner = Runner(tmp_config_file_three)
    monkeypatch.setattr(new_runner, 'logged_in', True)
    return new_runner
