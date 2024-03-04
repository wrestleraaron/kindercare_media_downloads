import getopt
import json
import os
import sys
import requests
from exif import Image
import ffmpeg

os.environ['REQUESTS_CA_BUNDLE'] = '/Users/aaron/ca_bundle.pem'

def usage() -> None:
    '''
    Print Usage
    '''
    print(f'Usage: {sys.argv[0]} [-cik xxxxxxx]')
    sys.exit(1)


def get_options(args: list) -> dict:
    '''
    Get Options
    '''
    options = "cik:"
    
# Long options
    long_options = [
        "metadata activity is added as caption below the picture",
        "ignore database - id of the downloaded media is not added to the local db",
        "child id value for the child's profile = "]
 
    try:
        arguments, _ = getopt.getopt(args, options, long_options)
        inputs = {
            'caption': 'False',
            'db_insert': 'True',
            'id': '0'
        }
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-c", "--metadata"):
                inputs['caption'] = 'True'
            elif currentArgument in ("-i", "--ignore_db"):
                inputs['db_insert'] = 'False'
            elif currentArgument in ("-k", "--id"):
                inputs['id'] = currentValue
            elif currentArgument in ("-h", "--help"):
                print('get help')

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
        usage()

    return inputs

def make_db_file(id: str, db_insert: str) -> None:
    if os.path.exists(f'{os.getcwd()}/{id}'):
        print(f'{os.getcwd()}/{id} exists, if file can be accessed')

        if db_insert == 0: # user wants to update the db, check we can write to it
            if os.access(f'{os.getcwd()}/{id}/id.db', os.W_OK):
                print(f'{os.getcwd()}/{id}/id.db exists and is writable.')
            else:
                print(f'{os.getcwd()}/{id}/id.db exists but is not writable.\
                    Downloaded media will not be added to db')
    else:
        try: 
            os.makedirs(f'{os.getcwd()}/{id}')
            print(f'{os.getcwd()}/{id}')
        except OSError as oserr:
            print(f'Cannot create db folder: {oserr}')
            sys.exit(2)
    
        try:
            if os.path.isfile(f'{os.getcwd()}/{id}/id.db'):
                if os.access(f'{os.getcwd()}/{id}/id.db', os.W_OK):
                    print("The file exists and is writable.")
                else:
                    print("The file exists but is not writable.")
            else:
                # Create the file
                with open(f'{os.getcwd()}/{id}/id.db', "w") as f:
                    f.write("0")
                print("The file was created and is writable.")
        except OSError as oserr:
            print(f'Cannot create db file: {oserr}')
            sys.exit(2)



def get_db_entries(filename: str) -> set:
    '''
    Get all the db entries
    '''
    try:
        return set(open(filename).read().split())
    except Exception as oserr:
        print(f'OS Error: {oserr}')
        sys.exit(3)


def connect_to_kc(id: str):
    '''
    Connect to ?KC and get the data
    '''
    count = 1
    cookies = {'_himama_session': '9ce5617e0e62c76e34ea7512b0a3cd87'}
    try:
        req = requests.get(f'https://classroom.kindercare.com/accounts/{id}/journal_api?page={count}',
                       cookies=cookies,
                       timeout=30)
        req.raise_for_status()
    except Exception as err:
        print(f'ERROR: {err}')
        sys.exit(1)
    return req.json()


def get_kcdata(json_data:dict, id_set: set) -> dict:
    '''
    get data from kc for images/videos
    '''
    media_files = {}
    for day, data in json_data['intervals'].items():
        for item in enumerate(data):
            if f"{item[1]['activity']['id']}" in id_set:
                next
            else:
                activity_id = item[1]['activity']['id']
                title = item[1]['activity']['title']
                if title == '':
                    title = "Look what I'm doing today!"
                desc = item[1]['activity']['description']
                if desc == '':
                    desc = title
                create_date = item[1]['activity']['created_at']
                image = item[1]['activity']['image']['big']['url']
                video = item[1]['activity']['video']['url']
            # print(f'{activity_id}, {title}, {desc}, {create_date}, {image}, {video}')
                media_files[activity_id] = {
                                            'title': title,
                                            'desc': desc,
                                            'create_date': create_date,
                                            'image': image,
                                            'video': video
                                            }
    return media_files

def get_images_videos(media_info:dict, id_num: str):
    '''
    Get images
    '''
    ids_downloaded = set()
    for id, data in media_info.items():
        if data['image'] != None:
            date = data['create_date'].replace(':', '_')
            try:
                req = requests.get(data['image'], timeout=30)
                filename = f'{os.getcwd()}/{id_num}/{date}.jpg'
                req.raise_for_status()
                open(filename, 'wb').write(req.content)
                update_exif_data(filename, data)
                ids_downloaded.add(int(id))
            except Exception as err:
                print(f'unable to get image {data["image"]: {req.status_code}}')
        else:
            print(f'No Image found in {id}')
        if data['video'] != None:
            date = data['create_date'].replace(':', '_')
            try:
                req = requests.get(data['video'], verify=False)
                filename = f'{os.getcwd()}/{id_num}/{date}.mov'
                req.raise_for_status()
                open(filename, 'wb').write(req.content)
                # update_exif_data(filename, data)
                ids_downloaded.add(int(id))
            except Exception as err:
                print(f'unable to get image {data["image"]: {req.status_code}}')
        else:
            print(f'No Video found in {id}')
    return ids_downloaded

def update_db_info(id:set):
    '''
    Update db
    '''
    filename = f'{os.getcwd()}/{getopts["id"]}/id.db'
    current_db = set(open(filename).read().split())
    current_db.update(id)
    with open(filename, 'w', encoding='utf-8') as id_db:
        for id in current_db:
            id_db.write(f'{id}\n')


def update_exif_data(filename: str, media_info:dict):
    # with open(filename, 'rb') as image:
    with open(filename, 'rb') as image_file:
        image = Image(image_file)
        image.XPcomment = media_info['desc']
        image.Title = media_info['title']
        image.DateTimeOriginal = media_info['create_date']
    with open(filename, 'wb') as new_image:
        try:
            new_image.write(image.get_file())
        except Exception as err:
            print(f'ERROR:  {err}')

def update_video_data(filename: str, media_info:dict):
    input_stream = ffmpeg.input(filename)
    input_stream = input_stream.output(filename, metadata={'title': media_info['title']})
    ffmpeg.run(input_stream)



getopts = get_options(sys.argv[1:])

make_db_file(getopts['id'], getopts['db_insert'])

db_ids = get_db_entries(f'{os.getcwd()}/{getopts["id"]}/id.db')
kc_web_data = connect_to_kc(getopts['id'])
kc_media = get_kcdata(kc_web_data, db_ids)
new_ids = get_images_videos(kc_media, getopts['id'])
update_db_info(new_ids)