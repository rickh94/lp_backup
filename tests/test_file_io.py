from lp_backup import file_io
import pytest
import fs


@pytest.fixture
def test_backup_data():
    lines = [f"url{i},username{i},password{i}" for i in range(1, 30)]
    return '\n'.join(lines).encode('utf-8')


def test_write_out_backup(tmpdir_factory, test_backup_data):
    testdir = [tmpdir_factory.mktemp(f"write_out_backup_{i}") for i in range(0, 5)]
    back_fs = [fs.open_fs(str(dir_)) for dir_ in testdir]
    outfile = [f"today-email-number{i}" for i in range(0, 4)]
    file_io.write_out_backup([back_fs[0], back_fs[1]], test_backup_data, outfile[0])
    back_fs[2].makedir('hi')
    file_io.write_out_backup(backing_store_fs=back_fs[2], data=test_backup_data, outfile=outfile[1], prefix='hi/')
    file_io.write_out_backup(back_fs[3], test_backup_data, outfile[2], prefix='hi')
    file_io.write_out_backup(back_fs[4], test_backup_data, outfile[3])
    assert outfile[0] in back_fs[0].listdir('/')
    with back_fs[0].open(outfile[0]) as test_file:
        assert "url1,username1,password1" in test_file.read()

    assert outfile[0] in back_fs[1].listdir('/')
    with back_fs[1].open(outfile[0]) as test_file:
        assert "url1,username1,password1" in test_file.read()

    assert outfile[1] in back_fs[2].listdir('/hi/')
    with back_fs[2].open('hi/' + outfile[1]) as test_file:
        assert "url1,username1,password1" in test_file.read()

    assert outfile[2] in back_fs[3].listdir('/hi/')
    with back_fs[3].open('hi/' + outfile[2]) as test_file:
        assert "url1,username1,password1" in test_file.read()

    assert outfile[3] in back_fs[4].listdir('/')
    with back_fs[4].open(outfile[3]) as test_file:
        assert "url1,username1,password1" in test_file.read()

    for fs_ in back_fs:
        fs_.close()


def test_read_backup(tmpdir_factory, test_backup_data):
    testdir = [tmpdir_factory.mktemp(f"read_backup_{i}") for i in range(0, 3)]
    back_fs = [fs.open_fs(str(dir_)) for dir_ in testdir]
    outfile = [f"today-email-number{i}" for i in range(0, 3)]
    for i in range(0, 3):
        with back_fs[i].open(outfile[i], 'wb') as test_file:
            test_file.write(test_backup_data)
        data_found = file_io.read_backup(back_fs[i], outfile[i])
        assert data_found == test_backup_data
    back_fs_prefix = fs.open_fs(str(tmpdir_factory.mktemp(f"read_backup_4")))
    test_prefix = 'hi'
    outfile_prefix = "today-email-number3"
    back_fs_prefix.makedir('hi')
    with back_fs_prefix.open('hi/' + outfile_prefix, 'wb') as test_file:
        test_file.write(test_backup_data)
    prefix_data_found = file_io.read_backup(back_fs_prefix, outfile_prefix, test_prefix)
    assert prefix_data_found == test_backup_data

