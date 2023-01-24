from tqdm import tqdm
import pandas as pd
from PIL import Image
import requests
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.contrib import gce
from googleapiclient.http import MediaFileUpload

users = {'user_1':'user_1_id', 'user_2':'user_2_id', 'user_3':'user_3_id', 'user_4':'user_4_id', 'user_5':'user_5_id', 'user_6':'user_6_id'}

CLIENT_SECRET = ".\\credentials\\token1.json"

SCOPES='https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('.\\credentials\\token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
    creds = tools.run_flow(flow, store)
SERVICE = build('drive', 'v3', http=creds.authorize(Http()))
SS_SERVICE = build('sheets', 'v4', http=creds.authorize(Http()))

africans = {'africans':'africans_id'}
caucasians = {'caucasians':'caucasians_id'}
east_asia = {'east_asia':'east_asia_id'}
hispanic = {'hispanic':'hispanic_id'}
middle_east = {'middle_east':'middle_east_id'}
south_asia = {'south_asia':'south_asia_id'}

date_dir = '10'

list_of_ethnos_dirs = [africans, caucasians, east_asia, hispanic, middle_east, south_asia]

# query = "mimeType='application/vnd.google-apps.folder' and trashed=false"

ethnos_with_date_dir = {}

# Собираем айди папки за нужное число в каждом этносе

for ethnos_dir in list_of_ethnos_dirs:
    ethnos_dir_id = [v for k,v in ethnos_dir.items()][0]
    ethnos_dir_name = [k for k,v in ethnos_dir.items()][0]
    query = f"parents = '{ethnos_dir_id}'"
    results = SERVICE.files().list(q=query, fields="nextPageToken, files(id, name)", pageSize=1000, spaces='drive').execute()
    for dir in results['files']:
        if dir['name'] == date_dir:
            ethnos_with_date_dir[ethnos_dir_name] = dir['id']

print(ethnos_with_date_dir)

# Собираем айди всех папок в папке за нужное число в каждом этносе

all_dirs = {}

for ethnos_dir_name in ethnos_with_date_dir.keys():
    all_dirs_in_ethos_dir = []
    query = f"parents = '{ethnos_with_date_dir[ethnos_dir_name]}'"
    results = SERVICE.files().list(q=query, fields="nextPageToken, files(id, name)", pageSize=1000,spaces='drive').execute()
    if ethnos_dir_name != 'caucasians':
        for dir in results['files']:
            all_dirs_in_ethos_dir.append(dir)
        all_dirs[ethnos_dir_name] = all_dirs_in_ethos_dir
    else:
        two_caucasians_dirs = []
        for dir in results['files']:
            two_caucasians_dirs.append(dir)
        for caucasians_dir in two_caucasians_dirs:
            query = f"parents = '{caucasians_dir['id']}'"
            results = SERVICE.files().list(q=query, fields="nextPageToken, files(id, name)", pageSize=1000,spaces='drive').execute()
            for dir in results['files']:
                all_dirs_in_ethos_dir.append(dir)
            all_dirs[ethnos_dir_name] = all_dirs_in_ethos_dir

print(all_dirs)

df = pd.DataFrame(data={'Ethnocity':['africans', 'caucasians','east_asia','hispanic','middle_east','south_asia']}, columns = ['Ethnocity', 'user_1', 'user_2', 'user_3', 'user_4'])

for ethnos in all_dirs.keys():
    for dir in all_dirs[ethnos]:
        print(dir)
        break

#запрос для получения всех файлов в папке
# r = requests.get("https://www.googleapis.com/drive/v3/files?q='folder_id'+in+parents&fields=files(md5Checksum,+originalFilename)&key=user_key").json()
