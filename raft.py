from gdrive import GoogleDriveModule
from datetime import datetime
import os
import zipfile
from util import openAndReadFile, confirmationInput

class RaftSaver:
  def __init__(self, world_path: str, driveModule: GoogleDriveModule) -> None:
    self.world_path = world_path
    self.gdrive = driveModule

  def selectWorldFromLocal(self):
    os.system(f"dir /b {self.world_path} > out.txt")
    for world in openAndReadFile("out.txt"):
      if(confirmationInput(f"Select this world `{world}`? (y/N):")):
        return world
    raise ValueError("ERROR: No world Selected")

  def save(self) -> None:
    world_name = ""
    try:
      world_name = self.selectWorldFromLocal()
    except ValueError as err:
      raise err

    filename = f"{world_name}-saved.zip"
    filepath = os.path.join(self.world_path, f'"{world_name}"')

    os.system(f'xcopy {filepath} temp\\ /EY > out.txt')
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
      for root, _, files in os.walk("temp"):
        for file in files:
          zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join("temp", '..')))

    if not os.path.isfile(os.path.join(os.path.curdir, filename)):
      raise BaseException("Create Zip ERROR")

    os.system(f"rd /s /q temp")
    os.system("dir /b")

  def load(self) -> None:
    # download and apply save data
    pass
