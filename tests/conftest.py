import pytest

def pytest_addoption(parser):
  parser.addoption("--username", action="store", help="BpmSupreme username login", required=True)
  parser.addoption("--password", action="store", help="BpmSupreme password login", required=True)

@pytest.fixture
def username(request):
  return request.config.getoption("--username")

@pytest.fixture
def password(request):
  return request.config.getoption("--password")