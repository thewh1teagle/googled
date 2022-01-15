import os.path
import io
import pathlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import googleapiclient
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class Drive:
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.appdata',
        'https://www.googleapis.com/auth/drive.scripts',
        'https://www.googleapis.com/auth/drive.metadata'
    ]


    def __init__(self, creds = None) -> None:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not os.path.exists('credentials.json'):
            raise Exception('credentials.json not found!')

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        self.drive: googleapiclient.discovery.Resource = build(
            'drive', 'v3', credentials=creds)

    def listFiles(self, show_output=True):
        results = self.drive.files().list(
            pageSize=20, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            if show_output:
                for item in items:
                    print(u'{0} {1}'.format(item['name'], item['id']))
        return items

    def downloadFile(self, file_id, filepath):
        request = self.drive.files().get_media(fileId=file_id)
        # get_media is not appearing on any documentation, we need namereq for getting the metadata
        namereq = self.drive.files().get(
            fileId=file_id, supportsTeamDrives=True).execute()
        print('Pulling', namereq['name'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
        with io.open(filepath, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
        return done

    def uploadFile(self, filename, filepath, mimetype=None):
        import magic  # https://github.com/ahupp/python-magic
        file_metadata = {'name': filename}
        if mimetype == None:
            mimetype = magic.from_file(filepath, mime=True)
        media = MediaFileUpload(filepath,
                                mimetype=mimetype)
        file = self.drive.files().create(body=file_metadata,
                                         media_body=media,
                                         fields='id').execute()
        print('File ID: {}'.format(file.get('id')))
        return file.get('id')

    def create_folder_if_not_exist(self, name):
        folders = self.listFiles(show_output=False)
        folder = next((i['id'] for i in folders if i['name'] == name), None)
        if folder:
            print('Folder already exist')
            return folder

        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.drive.files().create(body=file_metadata,
                                         fields='id').execute()
        print('Folder ID of {}: {} \n'.format(name, file.get('id')))
        return file.get('id')

    def searchFile(self, query, size=1, TeamDriveId=None, folderId=None):
        corporaParam = None
        if TeamDriveId != None:
            corporaParam = 'drive'
        results = self.drive.files().list(
            pageSize=size,
            fields="nextPageToken, files(id, name, kind,modifiedTime,mimeType,parents,driveId)",
            q=query, supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            driveId=TeamDriveId, corpora=corporaParam).execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            for item in items:
                print('{} ({})'.format(item['name'], item['id']))
                print(item)
        return items

    def searchFileByName(self, fileName, size=1, TeamDriveId=None, folderId=None):
        corporaParam = None
        query = f"name contains '{fileName}'"
        if TeamDriveId != None:
            corporaParam = 'drive'
        results = self.drive.files().list(
            pageSize=size,
            fields="nextPageToken, files(id, name, kind,modifiedTime,mimeType,parents,driveId)",
            q=query, supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            driveId=TeamDriveId, corpora=corporaParam).execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            return None
        else:
            itemId = None
            for item in items:
                if (item['name'] == fileName):
                    for folder in item['parents']:
                        if folder == folderId:
                            print(
                                '{0} - ({1})'.format(item['name'], item['id']))
                            itemId = str(item['id'])
            if itemId == None:
                print('No files found by your criteria.')
            return itemId

    def move_file(self, file_id, final_drive_path, copy=False):
        # https://stackoverflow.com/questions/40725769/move-a-file-with-google-drive-api
        """Moves a file in Google Drive from one location to another.
        service: Drive API service instance.
        'filename' (string): file path on local machine, or a bytestream
        to use as a file.
        'init_drive_path' (string): the file path the file was initially in on Google
        Drive (in <folder>/<folder>/<folder> format).
        'drive_path' (string): the file path to move the file in on Google
        Drive (in <folder>/<folder>/<folder> format).
        'copy' (boolean): file should be saved in both locations
        Returns nothing.
        """
        # if init_drive_path == 'root':
        #    get_root_id = drive.files().get(fileId=init_drive_path).execute()
        #    folder_id = namereq['id']

        if not file_id or not final_drive_path:
            raise Exception(
                'Did not find file specefied: {}/{}'.format(file_id, final_drive_path))

        file = self.drive.files().get(fileId=file_id,
                                      fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))

        if copy:
            previous_parents = ''

        file = self.drive.files().update(fileId=file_id,
                                         supportsTeamDrives=True,
                                         addParents=final_drive_path,
                                         removeParents=previous_parents,
                                         fields='id, parents').execute()
        return True

    def upload2_folder_by_id(self, fileName, destfolder_id, MimeType=None):
        notUploaded = True
        while notUploaded is True:
            try:
                driveFileId = self.uploadFile(
                    filename=fileName, filepath=fileName, mimetype=MimeType)
                if self.move_file(driveFileId, destfolder_id):
                    notUploaded = False
            except ConnectionAbortedError:
                print('ConnectionAbortedError: Re-connecting again...')
                self.connect2service()
                
        print(f'{fileName} uploaded to https://drive.google.com/file/d/{driveFileId}/')

    def upload2_folder_by_name(self, fileName, destFolderName):
        destfolder = next(
            (item for item in self.listFiles(show_output=False) if item['name'] == destFolderName), None)
        if not destfolder:
            raise Exception(f'Not found {destFolderName} folder')
        self.upload2_folder_by_id(fileName, destfolder['id'])

    def upload_file_in_folder(self, drive_folder_id, local_file_name, local_file_path, percent_show):
        # drive_folder_id = folderid
        file_metadata = {
            'name': local_file_name,
            'parents': [drive_folder_id]
        }
        media = MediaFileUpload(local_file_path,
                                mimetype='application/octet-stream',
                                resumable=True)
        file = self.drive.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        print('File ID of {}: {}  ({}% Completed...) '.format(
            local_file_name, file.get('id'), int(percent_show)))
        print("")


def creating_folder_in_parent_folder(self, local_folder_name, parent_folder_id):

    file_metadata = {
        'name': local_folder_name,
        'parents': [parent_folder_id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = self.drive.files().create(body=file_metadata,
                                        fields='id').execute()
    print('Folder ID of {}: {} \n'.format(local_folder_name, file.get('id')))
    return file.get('id')


def upload_all_files_of_given_folder(self, local_folder_path, local_folder_name, drive_folder_id, folder_size_calculated):

    global file_size_counter

    for root, dirs, files in os.walk(local_folder_path):
        for single_file_name in files:
            current_size = os.path.getsize(
                os.path.join(root, single_file_name))
            file_size_counter = file_size_counter + current_size
            percent = (float(file_size_counter)/folder_size_calculated)*100
            self.upload_file_in_folder(drive_folder_id, single_file_name, os.path.join(
                root, single_file_name), percent)
        break


def recursive_upload(self, local_folder_path, local_folder_name, drive_folder_id, folder_size):

    upload_all_files_of_given_folder(local_folder_path, local_folder_name, drive_folder_id, folder_size)

    id_list = {}
    for root, dirs, files in os.walk(local_folder_path):
        for single_dir_name in dirs:
            temp_id = creating_folder_in_parent_folder(single_dir_name, drive_folder_id)
            id_list[single_dir_name] = temp_id
        break

    for key, value in id_list.items():
        new_path = os.path.join(local_folder_path, key)
        recursive_upload(new_path, key, value, folder_size)


def get_directory_size(p):
    root_directory = pathlib.Path(p)
    return sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())

def whole_folder_upload(self, local_folder_path, local_folder_name):

    local_folder_whole_size = get_directory_size(local_folder_path)
    print("Total Folder size is {} Bytes.".format(local_folder_whole_size))
    print("")
    root_id = createFolder(local_folder_name)
    recursive_upload(local_folder_path, local_folder_name,
                     root_id, local_folder_whole_size)
def createFolder(self, name):
        file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.drive.files().create(body=file_metadata,
                                            fields='id').execute()
        print('Folder ID: {}'.format(file.get('id')))
        return file.get('id') 