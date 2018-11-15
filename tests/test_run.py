import os
from cryptography.fernet import Fernet
from pathlib import Path
from unittest import mock
import subprocess

# from fs import open_fs
# import pytest
#
# from lp_backup import runner
# from lp_backup import exceptions

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


def test_config_file_read(test_runner_one, test_runner_two, test_runner_three):
    """Test reading configuration files correctly."""
    # test runner one
    assert test_runner_one.config["Email"] == "johnsmith@example.com"
    assert test_runner_one.config["Trust"] is True
    # assert test_runner_one.config["Encryption Key"] == "generate"
    assert test_runner_one.config["Compression"] is True
    assert test_runner_one.config["Backing Store"]["Type"] == "S3"
    assert test_runner_one.config["Backing Store"]["Bucket"] == "mybackupbucket"
    assert test_runner_one.config["Backing Store"]["Prefix"] == "backupfolder/"
    assert test_runner_one.config["Backing Store"]["Date"] is True
    # test runner two
    assert test_runner_two.config["Email"] == "johnsmith@example.com"
    assert test_runner_two.config["Trust"] is True
    assert test_runner_two.config["Encryption Key"] is None
    assert test_runner_two.config["Compression"] is True
    assert test_runner_two.config["Backing Store"]["URI"] == "/tmp/mybackup"
    assert test_runner_two.config["Backing Store"]["Prefix"] == "hi"
    assert test_runner_two.config["Backing Store"]["Date"] is True
    # test runner three
    assert test_runner_three.config["Email"] == "johnsmith@example.com"
    assert test_runner_three.config["Trust"] is False
    # assert test_runner_three.config["Encryption Key"] ==
    # assert test_runner_three.fernet == Fernet("d0RlMDVhd29jek5hUmpSNzJxXy1Ba01aZzBYMy16TElQbm9Qc2JyUXp5QT0=")
    assert test_runner_three.config["Compression"] is False
    assert test_runner_three.config["Backing Store"]["Type"] == "S3"
    assert test_runner_three.config["Backing Store"]["Bucket"] == "testbackupspace"
    assert test_runner_three.config["Backing Store"]["Endpoint URL"] == "https://nyc3.digitaloceanspaces.com"
    assert test_runner_three.config["Backing Store"]["Key ID"] == "$DOKEY"
    assert test_runner_three.config["Backing Store"]["Secret Key"] == "$DOSECRET"
    assert test_runner_three.config["Backing Store"].get("Prefix", "") == ""
    assert test_runner_three.config["Backing Store"].get("Date", False) is False


def test_configure_encryption(test_runner_one, test_runner_two, test_runner_three):
    """Tests the correct configuration of encryption for various settings."""
    assert isinstance(test_runner_one.fernet, Fernet)
    assert test_runner_two.fernet is None
    assert isinstance(test_runner_three.fernet, Fernet)


def test_login(test_runner_one, test_runner_two, test_runner_three):
    # assert test_runner_one.sultan.lpass.assert_called_with("login", "johnsmith@example.com",
    #                                                             "--trust")
    mock_run = mock.MagicMock()
    mock_return = mock.MagicMock()
    mock_return.stderr = ""
    mock_return.stdout = ["Success: "]
    mock_run.return_value = mock_return
    with mock.patch("subprocess.run", mock_run):
        test_runner_one.login()
        mock_run.assert_called_once_with(["lpass", "login", "johnsmith@example.com", "--trust"], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        mock_run.reset_mock()
        test_runner_two.login()
        mock_run.assert_called_once_with(["lpass", "login", "johnsmith@example.com", "--trust"],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_run.reset_mock()
        test_runner_three.login()
        mock_run.assert_called_once_with(["lpass", "login", "johnsmith@example.com", ""],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# def test_configure_backing_store(testrunner, monkeypatch, bad_testrunner):
#     testfs1 = testrunner._configure_backing_store()
#     assert testfs1._bucket_name == 'mybackupbucket'
#     assert testfs1.aws_access_key_id is None
#     assert testfs1.aws_secret_access_key is None
#     assert testfs1.endpoint_url is None
#     assert testfs1.strict is False
#     testfs1.close()
#
#     monkeypatch.setenv('DOKEY', 'testkeyid')
#     monkeypatch.setenv('DOSECRET', 'testsecretkey')
#     test2runner = runner.Runner(str(Path(DATA, 'testconf-2.yml')))
#     testfs2 = test2runner._configure_backing_store()
#     assert testfs2._bucket_name == 'testbackupspace'
#     assert testfs2.aws_access_key_id == 'testkeyid'
#     assert testfs2.aws_secret_access_key == 'testsecretkey'
#     assert testfs2.endpoint_url == 'https://nyc3.digitaloceanspaces.com'
#     assert testfs2.strict is False
#     testfs2.close()
#
#     test3runner = runner.Runner(str(Path(DATA, 'testconf-3.yml')))
#     testfs3 = test3runner._configure_backing_store()
#     assert testfs3.root_path == '/tmp/testbackupdir'
#     testfs3.close()
#     assert os.path.exists('/tmp/testbackupdir')
#     assert os.path.isdir('/tmp/testbackupdir')
#
#     with pytest.raises(ConfigurationError):
#         bad_testrunner._configure_backing_store()
#
#
# def test_package(testrunner, tmpdir, table_names):
#     testfile = Path(tmpdir, 'testtar.tar')
#     testrunner._save_tables()
#     testrunner._package(str(testfile))
#     testtar = open_fs(f"tar://{testfile}")
#     for name in table_names:
#         assert f"{_normalize(name)}.json" in testtar.listdir('/')
#
#
# def test_backup(testrunner, bad_testrunner, tmpdir, monkeypatch):
#     dirnumber = [0]
#     def localfs(*args):
#         name = f"backup{dirnumber[0]}"
#         path = Path(tmpdir, name)
#         dirnumber[0] += 1
#         return open_fs(str(path), create=True)
#     monkeypatch.setattr(testrunner, '_configure_backing_store', localfs)
#     testrunner.backup()
