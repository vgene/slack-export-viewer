import os
import requests
import time
import tqdm
from multiprocessing import Pool

def fetch_url(uri_and_name):
    uri, fname = uri_and_name
    path = "files/" + fname
    if not os.path.exists(path):
        r = requests.get(uri, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            print("download fail for ", uri)

    time.sleep(0.5)

if __name__ == '__main__':
    with open("./download.txt", 'r') as fd:
        urls_and_names = fd.readlines()

    urls_and_names = [tuple(s.strip().split(' ')) for s in urls_and_names]


    pool = Pool(processes=8)
    for _ in tqdm.tqdm(pool.imap_unordered(fetch_url, urls_and_names), total=len(urls_and_names)):
        pass
    pool.close()
