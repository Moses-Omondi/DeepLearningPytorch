import os
import sys
import urllib3
from urllib.parse import urlparse
import pandas as pd
import itertools
import shutil

from urllib3.util import Retry

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define classes and set types
classes = ["cat", "fish"]
set_types = ["train", "test", "val"]

def download_image(url, klass, data_type):
    basename = os.path.basename(urlparse(url).path)
    filename = "{}/{}/{}".format(data_type, klass, basename)

    # Create the directory if it does not exist
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    # Check if file already exists
    if not os.path.exists(filename):
        try:
            http = urllib3.PoolManager(retries=Retry(connect=1, read=1, redirect=2))
            with http.request("GET", url, preload_content=False) as resp, open(filename, "wb") as out_file:
                if resp.status == 200:
                    shutil.copyfileobj(resp, out_file)
                    print(f"Downloaded {url} to {filename}")
                elif 400 <= resp.status < 600:  # Check for 400-500 range errors
                    print(f"Error downloading {url}: Status code {resp.status}. Deleting {filename}.")
                    # Delete the image if it exists, and we encountered an error
                    if os.path.exists(filename):
                        os.remove(filename)
                    return  # Early return on error
                else:
                    print(f"Unexpected status code {resp.status} for {url}.")
                    return  # Early return for unexpected status codes
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            # Remove the file if it exists
            if os.path.exists(filename):
                os.remove(filename)
            return  # Early return on error

if __name__ == "__main__":
    if not os.path.exists("images.csv"):
        print("Error: can't find images.csv!")
        sys.exit(0)

    # Load images data from CSV
    imagesDF = pd.read_csv("images.csv")

    # Create directories for each class and set type
    for set_type, klass in itertools.product(set_types, classes):
        path = "./{}/{}".format(set_type, klass)
        if not os.path.exists(path):
            print("Creating directory {}".format(path))
            os.makedirs(path)

    print("Downloading {} images".format(len(imagesDF)))

    # Download images and handle errors
    result = [
        download_image(url, klass, data_type)
        for url, klass, data_type in zip(
            imagesDF["url"], imagesDF["class"], imagesDF["type"]
        )
    ]
    
    print("Finished downloading images.")
    sys.exit(0)
