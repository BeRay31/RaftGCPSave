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
  def __init__(self, creds, save_folder_name, force_create, is_shared) -> None:
    oAuthCreds = None

    if os.path.exists('token.json'):
      oAuthCreds = Credentials.from_authorized_user_file('token.json', SCOPES_PERMISSION)

    if not oAuthCreds or not oAuthCreds.valid:
      if oAuthCreds and oAuthCreds.expired and oAuthCreds.refresh_token:
        oAuthCreds.refresh(Request())
      else:
        flowAuth = InstalledAppFlow.from_client_config(
          client_config=json.loads(base64.b64decode(creds)),
          scopes=SCOPES_PERMISSION
        )
        oAuthCreds = flowAuth.run_local_server(port=0)
      with open('token.json', 'w') as token:
        token.write(oAuthCreds.to_json())
    self.driveService = build('drive', 'v3', credentials=oAuthCreds)
    self.raftFolderId = self.getOrCreateRaftFolderId(save_folder_name, force_create, is_shared)
  
  def getOrCreateRaftFolderId(self, save_folder_name: str, force_create: bool, is_shared: bool) -> str:
    query = f"mimeType='application/vnd.google-apps.folder' and name='{save_folder_name}' and trashed = false"
    if is_shared:
      query += "and sharedWithMe"
    response = self.driveService.files().list(
      q=query,
      spaces='drive',
      fields='files(id, name)'
    ).execute()
    print(response)
    for file in response.get('files', []):
      return file.get("id")

    # not found | create new one
    if force_create:
      file_metadata = {
        'name': save_folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
      }

      file = self.driveService.files().create(
        body=file_metadata,
        fields='id'
      ).execute()

      return file.get('id')

    raise Exception("Failed load save folder: No folder found")

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
      self.driveService.files().delete(fileId=id).execute()
      print(f"Deleted duplicate save file with Id {id}")

    file_meta = {
      'name': filename,
      'parents': [self.raftFolderId]
    }

    media = MediaFileUpload(
      filepath,
      mimetype
    )

    response = self.driveService.files().create(
      body=file_meta,
      media_body=media,
      fields='id, owners(emailAddress)'
    ).execute()

    # Edit filename
    finalname = f"{filename}-{response.get('owners')[0].get('emailAddress')}"
    ids = self.getSpecificFilenameIds(finalname)
    for id in ids:
      self.driveService.files().delete(fileId=id).execute()
      print(f"Deleted duplicate named save file with Id {id}")
    newBody = { 'name': finalname }
    # Update meta
    self.driveService.files().update(fileId=response.get('id'), body=newBody).execute()

    print(f"File '{filepath}' has been uploaded as '{finalname}' with Id: {response.get('id')}")
    return response.get('id')


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
