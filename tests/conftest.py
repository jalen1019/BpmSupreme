import pytest

def pytest_addoption(parser):
  parser.addoption("--username", action="store", help="BpmSupreme username login", required=True)
  parser.addoption("--password", action="store", help="BpmSupreme password login", required=True)
  parser.addoption("--song-name", action="store", help="BpmSupreme song to download", required=False)
  parser.addoption("--download-dir", action="store", help="BpmSupreme download directory")

@pytest.fixture
def username(request):
  return request.config.getoption("--username")

@pytest.fixture
def password(request):
  return request.config.getoption("--password")

@pytest.fixture
def song_name(request):
  return request.config.getoption("--song-name")

@pytest.fixture
def download_dir(request):
  return request.config.getoption("--download-dir")