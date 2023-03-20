from __future__ import print_function

import base64
import json
import os
import io

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

SCOPES_PERMISSION = [
  'https://www.googleapis.com/auth/drive'
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
    self.raftFolderId = self.getOrCreateRaftFolderId()
  
  def getOrCreateRaftFolderId(self) -> str:
    response = self.driveService.files().list(
      q="mimeType='application/vnd.google-apps.folder' and name='RaftSaveData' and trashed = false",
      spaces='drive',
      fields='files(id, name)'
    ).execute()

    for file in response.get('files', []):
      return file.get("id")

    # not found | create new one
    file_metadata = {
        'name': 'RaftSaveData',
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = self.driveService.files().create(
      body=file_metadata,
      fields='id'
    ).execute()

    return file.get('id')
  
  def getSpecificFilenameIds(self, filename) -> list:
    ids = []
    response = self.driveService.files().list(
      q=f"name='{filename}' and mimeType='application/zip' and trashed = false",
      spaces='drive',
      fields='files(id, name)'
    ).execute()
    for file in response.get('files', []):
      print(F'Found file: {file.get("name")}, {file.get("id")}')
      ids.append(file.get("id"))

    return ids

  def getAllSaveFileIds(self) -> list:
    saveFiles = []
    page_token = None
    while True:
      response = self.driveService.files().list(
        q=f"'{self.raftFolderId}' in parents and mimeType='application/zip' and trashed = false",
        spaces='drive',
        fields='nextPageToken, files(id, name)',
        pageToken=page_token
      ).execute()
      for file in response.get('files', []):
        saveFiles.append((file.get("id"), file.get("name")))
      page_token = response.get('nextPageToken', None)
      if page_token is None:
          break

    return saveFiles

  def uploadFile(self, filepath, mimetype, filename) -> None:
    ids = self.getSpecificFilenameIds(filename)
    for id in ids:
      print(f"Deleted duplicate save file with Id {id}")
      self.driveService.files().delete(fileId=id).execute()

    file_meta = {
      'name': filename,
      'parents': [self.raftFolderId]
    }

    media = MediaFileUpload(
      filepath,
      mimetype
    )

    file = self.driveService.files().create(
      body=file_meta,
      media_body=media,
      fields='id'
    ).execute()
    
    print(f"File '{filepath}' has been uploaded as '{filename}' with Id: {file.get('id')}")
    return file.get('id')


  def downloadFile(self, file_id, filename):
    request = self.driveService.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(F'Download {int(status.progress() * 100)}.')
    
    with open(filename, 'wb') as dest:
      dest.write(file.getvalue())

    return filename
