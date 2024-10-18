import json
import sys
import os.path
import urllib.request
import threading
import requests
from urllib.parse import unquote

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
    # Check if 'projectID' and 'fileID' are present in the element
    if 'projectID' not in element or 'fileID' not in element:
        print("Missing projectID or fileID in element:", element)
        return

    projectID = str(element['projectID'])
    fileID = str(element['fileID'])

    url = f'https://api.curse.tools/v1/cf/mods/{projectID}/files/{fileID}/download-url'
    
    try:
        # Set a User-Agent header
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        # Fetch the JSON response to get the raw download URL
        with urllib.request.urlopen(req) as response:
            download_info = json.load(response)
            raw_download_url = download_info['data']  # Extract the raw download URL
            
            # Decode the URL to handle encoded characters
            raw_download_url = unquote(raw_download_url)  # Decode the URL

        # Check if the file already exists
        filename = os.path.basename(raw_download_url)  # Extract filename from the URL
        if os.path.isfile(filename):
            print(f"File already exists: {filename}. Skipping download.")
            return  # Skip downloading if the file exists

        # Use the raw download URL to download the file
        response = requests.get(raw_download_url)  # Use requests to get the file
        with open(filename, 'wb') as f:  # Open the file in binary write mode
            f.write(response.content)  # Write the content to the file
        print(f"Downloaded file: {filename}")
        
        # Use a context manager for file writing
        with open(f"{filename}.url.txt", 'w') as f:
            f.write(raw_download_url)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} for URL: {url}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Create a list to hold threads
threads = []

for element in data['files']:
    # Create a new thread for each download
    thread = threading.Thread(target=download_file, args=(element,))
    threads.append(thread)  # Add the thread to the list
    thread.start()  # Start the thread

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Ensure proper termination
if all(not thread.is_alive() for thread in threads):
    print("Done!")
