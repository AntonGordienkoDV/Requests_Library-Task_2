import requests
import os
import datetime


class YaUploader:
    host = 'https://cloud-api.yandex.net'

    def __init__(self, _token: str):
        self.token = _token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self):
        url = f'{self.host}/v1/disk/resources'
        headers = self.get_headers()
        new_folder_path = '/upload_' + datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        params = {'path': new_folder_path}
        response = requests.put(url, headers=headers, params=params)
        if response.status_code in [201, 409]:
            print(f'\nCreating folder {new_folder_path} -> OK\n')
        return new_folder_path

    def _get_upload_link(self, path):
        url = f'{self.host}/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': path, 'overwrite': True}
        response = requests.get(url, headers=headers, params=params)
        return response.json().get('href')

    def upload_file(self, path, file_name):
        upload_link = self._get_upload_link(path)
        headers = self.get_headers()
        response = requests.put(upload_link, data=open(file_name, 'rb'), headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print(f'Uploading file {file_name} -> OK')

    def upload(self, file_path: str):
        upload_folder_path = self.create_folder()
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                upload_file_name = upload_folder_path + '/' + os.path.basename(file_path)
                self.upload_file(upload_file_name, file_path)
            elif os.path.isdir(file_path):
                files_list = os.listdir(file_path)
                print(f'Prepare files in {file_path} to upload:')
                print(*files_list, '', sep='\n')
                for file_name in files_list:
                    upload_file_name = upload_folder_path + '/' + file_name
                    self.upload_file(upload_file_name, os.path.join(file_path, file_name))


if __name__ == '__main__':
    # Получить путь к загружаемому файлу и токен от пользователя
    path_to_file = os.path.abspath(input('Enter path to file: ').strip())
    token = input('Enter your token: ').strip()

    uploader = YaUploader(token)
    uploader.upload(path_to_file)
