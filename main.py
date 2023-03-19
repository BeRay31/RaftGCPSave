import os
from util import openAndReadFile, confirmationInput
from gdrive import GoogleDriveModule
from dotenv import load_dotenv
from raft import RaftSaver

def clearOutput(filename):
  if (os.path.isfile("out.txt")):
    os.system("del out.txt")
  if (filename != "" and os.path.isfile(filename)):
    os.system(f"del {filename}")
  exit()

def getRaftFolder() -> str:
  path = os.path.join("", "C:", "Users")

  os.system(f"dir {path} /b > out.txt")
  user_target = ""
  for user in openAndReadFile('out.txt'):
    if confirmationInput(f"Is this your current windows user {user}? (y/N):"):
      user_target = user
      break
  if user_target == "":
    print("LOAD ERROR: No User Specified")
    clearOutput()

  toJoin = [path, user_target, "AppData", "LocalLow", '"Redbeet Interactive"', "Raft", "User"]
  return os.path.join(*toJoin)

def getWorldPath(raft_folder: str) -> str:
  os.system(f'dir {raft_folder} /b > out.txt')
  raft_user = openAndReadFile('out.txt')
  target_raft_user = ""
  if len(raft_user) == 1:
    target_raft_user = raft_user[0]
  else:
    for user in raft_user:
      if confirmationInput(f"Is this your raft user {user}? (y/N):"):
        target_raft_user = user
        break

  if target_raft_user == "":
    print("LOAD ERROR: No User Specified")
    clearOutput()
  return os.path.join(raft_folder, target_raft_user, "World")

if __name__ == "__main__":
  load_dotenv()
  BASE64_GOOGLE_CREDENTIALS = os.getenv("GOOGLE_API_CREDS_BASE64")
  drive_mod = GoogleDriveModule(BASE64_GOOGLE_CREDENTIALS)
  world_path = getWorldPath(getRaftFolder())
  saver = RaftSaver(driveModule=drive_mod, world_path=world_path)
  saver.save("CollabWorld")


  