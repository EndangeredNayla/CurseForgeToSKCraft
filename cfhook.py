import json
import sys
import os.path
import urllib.request
import threading

if len(sys.argv) == 1:
    print('You did not specify a manifest.json! Exiting...')
    exit()
else:
    json_file = sys.argv[1]
    if not os.path.isfile(json_file):
        print('The file you stated does not exist! Exiting...')
        exit()

json_data = open(json_file)
data = json.load(json_data)
json_data.close()

def download_file(element):
    projectID = str(element['projectID'])
    fileID = str(element['fileID'])

    url = f'https://minecraft.curseforge.com/projects/{projectID}/files/{fileID}/download'
    print(url)

    # Setting a user-agent because CurseForge doesn't allow us to download mods directly
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    
    filename, _ = urllib.request.urlretrieve(url)
    print(f"Downloaded file: {filename}")
    
    # Use a context manager for file writing
    with open(f"{filename}.url.txt", 'w') as f:
        f.write(url)

for element in data['files']:
    thread = threading.Thread(target=download_file, args=(element,))
    thread.start()

for thread in threading.enumerate():
    if thread is not threading.main_thread():
        thread.join()

print("Done!")
