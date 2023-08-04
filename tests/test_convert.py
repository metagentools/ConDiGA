import os
import subprocess
from pathlib import Path

import pytest

__author__ = "Vijini Mallawaarachchi and Yu Lin"
__copyright__ = "Copyright 2022, ConDiGA Project"
__license__ = "MIT"
__version__ = "0.2.1"
__maintainer__ = "Vijini Mallawaarachchi"
__email__ = "viji.mallawaarachchi@gmail.com"
__status__ = "Development"


TEST_ROOTDIR = Path(__file__).parent
EXEC_ROOTDIR = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def tmp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("tmp")


@pytest.fixture(autouse=True)
def workingdir(tmp_dir, monkeypatch):
    """set the working directory for all tests"""
    monkeypatch.chdir(tmp_dir)


def exec_command(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    """executes shell command and returns stdout if completes exit code 0

    Parameters
    ----------

    cmnd : str
      shell command to be executed
    stdout, stderr : streams
      Default value (PIPE) intercepts process output, setting to None
      blocks this."""

    proc = subprocess.Popen(cmnd, shell=True, stdout=stdout, stderr=stderr)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FAILED: {cmnd}\n{err}")
    return out.decode("utf8") if out is not None else None


def test_convert_version():
    """test condiga version"""
    cmd = "convert --help"
    exec_command(cmd)

def test_convert_kraken(tmp_dir):
    """test condiga version"""
    file_name = TEST_ROOTDIR / "data" / "Kraken" / "kraken.out"
    cmd = f"convert -i {file_name} -t kraken -o {tmp_dir}"
    exec_command(cmd)

def test_convert_blast(tmp_dir):
    """test condiga version"""
    file_name = TEST_ROOTDIR / "data" / "BLAST" / "blast.out"
    cmd = f"convert -i {file_name} -t blast -o {tmp_dir}"
    exec_command(cmd)