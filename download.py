import json
import os
import traceback
import argparse
from pprint import pprint

# https://files.slack.com/files-pri/T0LSRH8S1-F2UEBKJKX/fullsizerender.jpg?...token....
def handleFile(f):
    tu = None
    if 'url_private' in f:
        ori_url_private = f['url_private']
        if "files.slack" in ori_url_private:
            local_file = ori_url_private.split("?")[0][34:]
            local_file = local_file.replace("/", "-")
            f['url_private'] = "/static/files/" + local_file
            f['url_private_remote'] = ori_url_private
            tu = (ori_url_private, local_file)
    return tu 

def replaceAttachment(history):

    need_download = []

    def handleAndInclude(f):
        tu = handleFile(f)
        if tu:
            need_download.append(tu)
            
    for msg in history:
        if 'files' in msg:
            # get url private
            for f in msg['files']:
                handleAndInclude(f)
        if 'item' in msg:
            handleAndInclude(msg['item'])
        if 'file' in msg:
            handleAndInclude(msg['file'])
        if 'attachments' in msg:
            for a in msg['attachments']:
                if 'files' in a:
                    for f in a['files']:
                        handleAndInclude(f)

    return need_download 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, required=True)
    parser.add_argument("-m", "--modify", action='store_true')
    args = parser.parse_args()

    path = args.path
    modify_in_place = args.modify
    
    os.chdir(path)
    download_list = []
    for directory in sorted(os.listdir(".")):
        per_dir_list = []
        if not os.path.isdir(directory):
            continue
        try:
            os.chdir(directory)
            # get all json files

            for f in sorted(os.listdir(".")):
                if f.endswith(".json"):
                    with open(f, 'r') as fd:
                        history = json.load(fd)
                    daily_list = replaceAttachment(history)
                    per_dir_list.extend(daily_list)
                    if modify_in_place:
                        with open(f, 'w') as fd:
                            json.dump(history, fd, indent=4)

        except Exception as e:
            print(e)
            traceback.print_stack()


        download_list.extend(per_dir_list)
        os.chdir(path)

    # remove duplicate
    download_map = dict(download_list)

    with open("download.txt", 'w') as fd:
        fd.writelines([k + " " + v + '\n' for k, v in download_map.items()])


if __name__ == "__main__":
    main()
