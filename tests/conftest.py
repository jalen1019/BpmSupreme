import pytest

def pytest_addoption(parser):
  parser.addoption("--username", action="store", help="BpmSupreme username login", required=True)
  parser.addoption("--password", action="store", help="BpmSupreme password login", required=True)
  parser.addoption("--bad-song-name", action="store", help="Invalid BpmSupreme song to download", required=False)
  parser.addoption("--download-dir", action="store", help="BpmSupreme download directory")
  parser.addoption("--duplicate-song", action="store", help="Song name to check duplicate of using directory from --download-dir option")

@pytest.fixture
def username(request):
  return request.config.getoption("--username")

@pytest.fixture
def password(request):
  return request.config.getoption("--password")

@pytest.fixture
def bad_song_name(request):
  return request.config.getoption("--bad-song-name")

@pytest.fixture
def download_dir(request):
  return request.config.getoption("--download-dir")

@pytest.fixture
def duplicate_song(request):
  return request.config.getoption("--duplicate-song")