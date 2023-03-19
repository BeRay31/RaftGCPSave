from gdrive import GoogleDriveModule
from datetime import datetime
import os
import zipfile

class RaftSaver:
  def __init__(self, world_path: str, driveModule: GoogleDriveModule) -> None:
    self.world_path = world_path
    self.gdrive = driveModule
  
  def save(self, world_name: str) -> None:
    filename = f"{world_name}-{datetime.today().strftime('%Y-%m-%d')}.zip"
    filepath = os.path.join(self.world_path, world_name)
    os.system(f"xcopy  {filepath} {world_name}\\ /EY > out.txt")
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
      for root, _, files in os.walk(world_name):
        for file in files:
          zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(world_name, '..')))
    if not os.path.isfile(os.path.join(os.path.curdir, filename)):
      raise BaseException("Create Zip ERROR")
    os.system(f"rd /s /q {world_name}")

  def load(self) -> None:
    # download and apply save data
    pass
