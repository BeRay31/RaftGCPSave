from gdrive import GoogleDriveModule
from util import selectOptions
import os
import zipfile
from util import openAndReadFile
import time

class RaftSaver:
  def __init__(self, world_path: str, driveModule: GoogleDriveModule) -> None:
    self.world_path = world_path
    self.world_py_path = world_path.replace('"Redbeet Interactive"', 'Redbeet Interactive')
    self.gdrive = driveModule

  def selectWorldFromLocal(self):
    os.system(f"dir /b {self.world_path} > out.txt")
    worlds = openAndReadFile("out.txt")
    worlds.insert(0, "cancel")
    selected_world_index = selectOptions(worlds, "Select world to save: ")
    if selected_world_index != 0:
       return worlds[selected_world_index]
    else:
      raise Exception("Cancel action")

  def save(self) -> None:
    world_name = ""
    try:
      world_name = self.selectWorldFromLocal()
    except Exception as err:
      print(err)
      return

    filename = f"{world_name}-saved.zip"
    filepath = os.path.join(self.world_path, f'"{world_name}"')

    print(f"Zipping {world_name}...")
    os.system(f'xcopy {filepath} "{world_name}"\\ /EY > out.txt')
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
      for root, _, files in os.walk(world_name):
        for file in files:
          zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(world_name, '..')))

    if not os.path.isfile(os.path.join(os.path.curdir, filename)):
      raise BaseException("Create Zip ERROR")

    # Upload gdrive

    os.system(f'rd /s /q "{world_name}"')
    print(f"Saving Complete ({world_name})")
    time.sleep(1)

  def load(self) -> None:
    # download and apply save data
    world_name = '"Beray solo no cheat!"'
    world_name_py = "Beray solo no cheat!"

    if os.path.isdir(os.path.join(self.world_py_path, world_name_py)):
      os.system(f'rd /s /q {os.path.join(self.world_path, world_name)}')

    with zipfile.ZipFile(f"{world_name_py}-saved.zip", 'r') as zipf:
      zipf.extractall(self.world_py_path)

    if not os.path.isdir(os.path.join(self.world_py_path, world_name_py)):
      raise BaseException("Load Save ERROR")

    print(f"Load Complete ({world_name})")
    time.sleep(1)
