from distutils.core import setup
import py2exe

setup(
  console = [{'script': 'main.py'}],
  zipfile = None,
  packages = ['gdrive', 'raft', 'util'],
  name = 'MyProgram',
  options = {
    'py2exe': {
      'packages': ['gdrive', 'raft', 'util'],
      'includes': ['main'],
      'bundle_files': 1,
    }
  }
)
