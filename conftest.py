import hashlib
import os
import sys
from urllib.parse import urljoin

import pytest
import requests

TEST_DATA_URL = "https://cdat.llnl.gov/cdat/sample_data/"

def pytest_sessionstart(session):
    download_all_test_data()

def download_all_test_data():
    for x in ["test_big_data_files.txt", "test_data_files.txt"]:
        download_test_data(x)

def download_test_data(test_data_info):
    test_data_info_path = os.path.join("share", test_data_info)
    test_data_local_path = os.path.join(sys.prefix, "share", "cdat",
                                        "sample_data")

    if not os.path.exists(test_data_local_path):
        os.makedirs(test_data_local_path)

    with open(test_data_info_path) as fd:
        data = fd.readlines()

    for x in data[1:]:
        md5, name = x.split()

        local_file = os.path.join(test_data_local_path, name)

        remote_url = urljoin(TEST_DATA_URL, name)

        if os.path.exists(local_file):
            print(f"Skipping {remote_url}, already exists")

            continue

        print(f"Downloading {remote_url} to {local_file}")

        response = requests.get(remote_url, stream=True)

        response.raise_for_status()

        m = hashlib.md5()

        with open(local_file, "wb") as fd:
            for chunk in response.iter_content(2048):
                m.update(chunk)

                fd.write(chunk)

        assert m.hexdigest() == md5, f"Missmatch hash for {remote_url!r}"

if __name__ == "__main__":
    download_all_test_data()
