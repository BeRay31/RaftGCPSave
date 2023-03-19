from __future__ import print_function

import base64
import json
import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES_PERMISSION = [
  'https://www.googleapis.com/auth/drive.metadata.readonly'
]

class GoogleDriveModule:
  def __init__(self, BASE64_GOOGLE_CREDENTIALS) -> None:
    oAuthCreds = None

    if os.path.exists('token.json'):
      oAuthCreds = Credentials.from_authorized_user_file('token.json', SCOPES_PERMISSION)

    if not oAuthCreds or not oAuthCreds.valid:
      if oAuthCreds and oAuthCreds.expired and oAuthCreds.refresh_token:
        oAuthCreds.refresh(Request())
      else:
        flowAuth = InstalledAppFlow.from_client_config(
          client_config=json.loads(base64.b64decode(BASE64_GOOGLE_CREDENTIALS)),
          scopes=SCOPES_PERMISSION
        )
        oAuthCreds = flowAuth.run_local_server(port=0)
      with open('token.json', 'w') as token:
        token.write(oAuthCreds.to_json())

    self.driveService = build('drive', 'v3', credentials=oAuthCreds)
  
  def getFolderId(self) -> str:
    response = self.driveService.files().list(q="mimeType='application/vnd.google-apps.folder' and name='RaftSave'",
                                    spaces='drive',
                                    fields='files(id, name)').execute()
    for file in response.get('files', []):
      print(F'Found file: {file.get("name")}, {file.get("id")}')
      return file.get("id")

    return ""


