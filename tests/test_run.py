import datetime
import lzma
import os
from cryptography.fernet import Fernet
from pathlib import Path
import subprocess

import pytest
from freezegun import freeze_time
from unittest import mock

import fs
from fs import tempfs

webdav_available = False
try:
    import webdavfs
    from webdavfs.webdavfs import WebDAVFS
    webdav_available = True
except ModuleNotFoundError:
    pass

import fs_s3fs

from lp_backup import exceptions
from lp_backup import file_io
import lp_backup

HERE = os.path.dirname(__file__)
DATA = Path(HERE, 'testdata')


def test_config_file_read(test_runner_one, test_runner_two, test_runner_three,
                          test_runner_four):
    """Test reading configuration files correctly."""
    # test runner one
    assert test_runner_one.config["Email"] == "johnsmith@example.com"
    assert test_runner_one.config["Trust"] is True
    # assert test_runner_one.config["Encryption Key"] == "generate"
    assert test_runner_one.config["Compression"] is True
    assert test_runner_one.config["Backing Store"][0]["Type"] == "S3"
    assert test_runner_one.config["Backing Store"][0]["Bucket"] == "mybackupbucket"
    assert test_runner_one.config["Prefix"] == "backupfolder/"
    assert test_runner_one.config["Date"] is True
    # test runner two
    assert test_runner_two.config["Email"] == "johnsmith@example.com"
    assert test_runner_two.config["Trust"] is True
    assert test_runner_two.config["Encryption Key"] is None
    assert test_runner_two.config["Compression"] is True
    assert test_runner_two.config["Backing Store"][0]["URI"] == "/tmp/mybackup"
    assert test_runner_two.config["Backing Store"][1]["URI"] == "/tmp/mybackup2"
    assert test_runner_two.config["Prefix"] == "hi"
    assert test_runner_two.config["Date"] is True
    # test runner three
    assert test_runner_three.config["Email"] == "johnsmith@example.com"
    assert test_runner_three.config["Trust"] is False
    # assert test_runner_three.config["Encryption Key"] ==
    # assert test_runner_three.fernet == Fernet("d0RlMDVhd29jek5hUmpSNzJxXy1Ba01aZzBYMy16TElQbm9Qc2JyUXp5QT0=")
    assert test_runner_three.config["Compression"] is False
    assert test_runner_three.config["Backing Store"][0]["Type"] == "S3"
    assert test_runner_three.config["Backing Store"][0]["Bucket"] == "testbackupspace"
    assert test_runner_three.config["Backing Store"][0]["Endpoint URL"] == "https://nyc3.digitaloceanspaces.com"
    assert test_runner_three.config["Backing Store"][0]["Key ID"] == "$DOKEY"
    assert test_runner_three.config["Backing Store"][0]["Secret Key"] == "$DOSECRET"
    assert test_runner_three.config["Backing Store"][1]["URI"] == "/tmp/backup3"
    assert test_runner_three.config.get("Prefix", "") == ""
    assert test_runner_three.config.get("Date", False) is False
    # test runner four
    assert test_runner_four.config["Email"] == "johnsmith@example.com"
    assert test_runner_four.config["Trust"] is True
    assert test_runner_four.config["Compression"] is True
    assert test_runner_four.config["Backing Store"][0]["Type"] == "webdav"
    assert test_runner_four.config["Backing Store"][0]["Base URL"] == "https://mynextcloud.com"
    assert test_runner_four.config["Backing Store"][0]["Root"] == "remote.php/webdav"
    assert test_runner_four.config["Backing Store"][0]["Username"] == "john"
    assert test_runner_four.config["Backing Store"][0]["Password"] == "$WEBDAV_PASSWORD"
    assert test_runner_four.config["Prefix"] == "backupfolder/"
    assert test_runner_four.config["Date"] is True


def test_configure_encryption(test_runner_one, test_runner_two, test_runner_three, test_runner_four):
    """Tests the correct configuration of encryption for various settings."""
    assert isinstance(test_runner_one.fernet, Fernet)
    assert test_runner_two.fernet is None
    assert isinstance(test_runner_three.fernet, Fernet)
    assert isinstance(test_runner_four.fernet, Fernet)


@pytest.fixture
def mock_run():
    run = mock.MagicMock()
    mock_return = mock.MagicMock()
    mock_return.stderr = ""
    mock_return.stdout = "Success: ".encode('utf-8')
    run.return_value = mock_return
    return run


@pytest.fixture
def mock_run_backup():
    run = mock.MagicMock()
    mock_return = mock.MagicMock()
    mock_return.stderr = ""
    mock_return.stdout = '\n'.join(["some backup data", "more data", "yet more data"]).encode('utf-8')
    run.return_value = mock_return
    return run


def test_login(test_runner_one, test_runner_two, test_runner_three, mock_run):
    # assert test_runner_one.sultan.lpass.assert_called_with("login", "johnsmith@example.com",
    #                                                             "--trust")
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
    mock_fail = mock.MagicMock()
    mock_fail_return = mock.MagicMock()
    mock_fail_return.stderr = "this is supposed to fail"
    mock_fail.return_value = mock_fail_return
    mock_fail2 = mock.MagicMock()
    mock_fail_return2 = mock.MagicMock()
    mock_fail_return2.stderr = ""
    mock_fail_return2.stdout = "not logged in"
    mock_fail2.return_value = mock_fail_return2

    with pytest.raises(exceptions.LoginFailed):
        with mock.patch("subprocess.run", mock_fail):
            test_runner_one.login()
        with mock.patch("subprocess.run", mock_fail2):
            test_runner_two.login()


def make_temp_fs():
    return tempfs.TempFS()


def raise_key_error():
    raise KeyError()


@freeze_time("Jan 1st, 2000")
def test_backup(test_runner_one, test_runner_two, test_runner_three, mock_run_backup,
                mock_lzma, monkeypatch, tmpdir_factory):
    mock_write = mock.MagicMock()
    with monkeypatch.context() as m:
        m.setattr(test_runner_one, '_configure_backing_store', make_temp_fs)
        m.setattr(test_runner_two, '_configure_backing_store', make_temp_fs)
        m.setattr(test_runner_three, '_configure_backing_store', make_temp_fs)
        m.setattr(lzma, 'compress', mock_lzma)
        m.setattr(lp_backup.file_io, 'write_out_backup', mock_write)
        m.setattr(subprocess, 'run', mock_run_backup)

        test_runner_one.backup()
        mock_run_backup.assert_called_once_with(['lpass', 'export'], stderr=subprocess.PIPE,
                                                stdout=subprocess.PIPE)
        # test_runner_one.fernet.encrypt.assert_called_once()
        mock_lzma.assert_called_once()
        outfile = (datetime.datetime(2000, 1, 1).isoformat() + '-' + "johnsmith@example.com" +
                   "-lastpass-backup" + ".csv.encrypted.xz")
        mock_write.assert_called_once_with(backing_store_fs=mock.ANY, outfile=outfile,
                                           prefix="backupfolder/", data=mock.ANY)
        mock_lzma.reset_mock()
        mock_run_backup.reset_mock()
        mock_write.reset_mock()

        test_runner_three.backup()
        mock_run_backup.assert_called_once_with(['lpass', 'export'], stderr=subprocess.PIPE,
                                                stdout=subprocess.PIPE)
        # test_runner_one.fernet.encrypt.assert_called_once()
        mock_lzma.assert_not_called()
        outfile = ("johnsmith@example.com" +
                   "-lastpass-backup" + ".csv.encrypted")
        mock_write.assert_called_once_with(backing_store_fs=mock.ANY, outfile=outfile,
                                           prefix="", data=mock.ANY)

        # if there's a keyerror, it should raise a config error
        m.setattr(test_runner_three, '_configure_backing_store', raise_key_error)
        with pytest.raises(exceptions.ConfigurationError):
            test_runner_three.backup()

    # raise backupfailed if there is stderr
    mock_backup_fail = mock.MagicMock()
    mock_fail_return = mock.MagicMock()
    mock_fail_return.sterr = "somthing has gone wrong"
    mock_backup_fail.return_value = mock_fail_return

    with pytest.raises(exceptions.BackupFailed):
        with mock.patch("subprocess.run", mock_backup_fail):
            test_runner_one.backup()

    # test multiple backing fs
    mock_run_backup.reset_mock()
    tmp_fs1 = fs.open_fs(str(tmpdir_factory.mktemp('test_backup1')))
    tmp_fs2 = fs.open_fs(str(tmpdir_factory.mktemp('test_backup2')))

    def test_temp_backing_store(*args):
        return [tmp_fs1, tmp_fs2]

    def random_data(*args):
        return b'this is some random data'

    with monkeypatch.context() as m:
        m.setattr(test_runner_two, '_configure_backing_store', test_temp_backing_store)
        m.setattr(lzma, 'compress', random_data)
        m.setattr(subprocess, 'run', mock_run_backup)
        test_runner_two.backup()
        mock_run_backup.assert_called_once_with(['lpass', 'export'], stderr=subprocess.PIPE,
                                                stdout=subprocess.PIPE)
        # test_runner_one.fernet.encrypt.assert_called_once()
        outfile = (datetime.datetime(2000, 1, 1).isoformat() + '-' + "johnsmith@example.com" +
                   "-lastpass-backup" + ".csv.xz")
        assert outfile in tmp_fs1.listdir('hi')
        assert outfile in tmp_fs2.listdir('hi')
        with tmp_fs1.open(f'hi/{outfile}', 'rb') as backupfile:
            assert random_data() in backupfile.read()

        with tmp_fs2.open(f'hi/{outfile}', 'rb') as backupfile:
            assert random_data() in backupfile.read()


@mock.patch('lzma.decompress')
def test_restore(mock_lzma, test_runner_one, test_runner_two, test_runner_three, monkeypatch):
    mock_fernet = mock.MagicMock()
    for runner in [test_runner_three, test_runner_two, test_runner_one]:
        monkeypatch.setattr(runner, '_configure_backing_store', make_temp_fs)
        monkeypatch.setattr(runner, 'filesystem', mock.MagicMock())
        try:
            monkeypatch.setattr(runner.fernet, 'decrypt', mock_fernet)
        except AttributeError:
            # test_runner_two has no fernet
            if runner == test_runner_two:
                pass

    mock_read_backup = mock.MagicMock()
    mock_read_backup.return_value = "thisis,some\ncomma,separated\ndata,for,testing"
    monkeypatch.setattr(file_io, "read_backup", mock_read_backup)

    test_runner_one.restore("testfile1.csv.encrypted.xz", "restorefile.csv")
    mock_read_backup.assert_called_once_with(mock.ANY, "testfile1.csv.encrypted.xz", "backupfolder/")
    mock_lzma.assert_called_once()
    mock_fernet.assert_called_once()

    mock_read_backup.reset_mock()
    mock_lzma.reset_mock()
    mock_fernet.reset_mock()
    test_runner_two.restore("testfile1.csv.xz", "restorefile.csv")
    mock_read_backup.assert_called_once_with(mock.ANY, "testfile1.csv.xz", "hi")
    mock_lzma.assert_called_once()
    mock_fernet.assert_not_called()


def raise_oserror(*args, **kwargs):
    raise OSError()


def test_configure_backing_store(test_runner_one, test_runner_two, monkeypatch, test_runner_three, test_runner_four):
    testfs1 = test_runner_one._configure_backing_store()[0]
    assert testfs1._bucket_name == 'mybackupbucket'
    assert testfs1.aws_access_key_id is None
    assert testfs1.aws_secret_access_key is None
    assert testfs1.endpoint_url is None
    assert testfs1.strict is False
    testfs1.close()

    testfs2 = test_runner_two._configure_backing_store()
    assert testfs2[0].root_path == '/tmp/mybackup'
    assert testfs2[1].root_path == '/tmp/mybackup2'
    testfs2[0].close()
    testfs2[1].close()
    assert os.path.exists('/tmp/mybackup')
    assert os.path.exists('/tmp/mybackup2')
    assert os.path.isdir('/tmp/mybackup')
    assert os.path.isdir('/tmp/mybackup2')
    os.rmdir('/tmp/mybackup')
    os.rmdir('/tmp/mybackup2')

    with monkeypatch.context() as m:
        m.setenv('DOKEY', 'testkeyid')
        m.setenv('DOSECRET', 'testsecretkey')
        testfs3 = test_runner_three._configure_backing_store()[0]
        assert isinstance(testfs3, fs_s3fs.S3FS)
        assert testfs3._bucket_name == 'testbackupspace'
        assert testfs3.aws_access_key_id == 'testkeyid'
        assert testfs3.aws_secret_access_key == 'testsecretkey'
        assert testfs3.endpoint_url == 'https://nyc3.digitaloceanspaces.com'
        assert testfs3.strict is False
        testfs3.close()

    if webdav_available:
        with monkeypatch.context() as m:
            m.setenv('WEBDAV_PASSWORD', 'testpassword')
            testfs4 = test_runner_four._configure_backing_store()[0]
            assert isinstance(testfs4, WebDAVFS)
            assert testfs4.url == 'https://mynextcloud.com'
            assert testfs4.root == '/remote.php/webdav'
            assert testfs4.client.webdav.login == 'john'
            assert testfs4.client.webdav.password == 'testpassword'
            testfs4.close()
    else:
        with pytest.raises(exceptions.NoWebdav):
            m.setenv('WEBDAV_PASSWORD', 'testpassword')
            _ = test_runner_four._configure_backing_store()


    with monkeypatch.context() as m:
        m.setattr(fs, 'open_fs', raise_oserror)
        with pytest.raises(exceptions.ConfigurationError):
            test_runner_two._configure_backing_store()


def test_backup_and_restore(test_runner_one, monkeypatch, tmpdir_factory):
    backup_test_folder = tmpdir_factory.mktemp('test_backup_restore')
    backup_test_fs = fs.open_fs(str(backup_test_folder))
    restore_folder = tmpdir_factory.mktemp('test_restore_from_backup')

    def backup_restore_fs(*args):
        return backup_test_fs

    class BackupData:
        stdout = '\n'.join(["this,is,some,data,i", "can,verify,later", "if i want to"]).encode('utf-8')
        stderr = ""

    def backup_data(*args, **kwargs):
        return BackupData()

    with monkeypatch.context() as m:
        m.setattr(test_runner_one, '_configure_backing_store', backup_restore_fs)
        m.setattr(subprocess, 'run', backup_data)
        backup_file = test_runner_one.backup()
        restore_file = os.path.join(restore_folder, backup_file)
        test_runner_one.restore(backup_file, restore_file)
        with open(restore_file, 'rb') as restore:
            assert restore.read() == BackupData().stdout


