'''
Get Kindercare Media for child
'''
import getopt
import os
import pickle
import sys
import requests

HIMAMA_SESSION_ID = ''


def usage() -> None:
    '''
    Prints usage information and exits the script.

    This function displays a help message explaining how to use the script with
    optional command-line arguments. It then exits the program with an exit code
    of 1, indicating an error or invalid usage.

  Returns:
    None. The function primarily prints information and exits the script.
    '''
    print(f'Usage: {sys.argv[0]} [-cik xxxxxxx]')
    sys.exit(1)


def get_options(args: list[str]) -> dict[str, str]:
    '''
    Parses command-line arguments and returns a dictionary of options.

    This function takes a list of command-line arguments and processes them using the
    `getopt` module. It supports both short and long options and maps them to a
    dictionary with descriptive keys and string values representing the user's choices.

    Args:
        args: A list of command-line arguments (strings).

    Returns:
        A dictionary containing parsed options with the following keys:
          - `caption` (str): 'True' if the user wants metadata added as a caption,
                              'False' otherwise (default).
          - `db_insert` (str): 'True' if the downloaded media ID should be added
                              to the local database, 'False' otherwise (default).
          - `id` (str): The child ID value provided by the user using the '-k' or
                              '--id' option (default '0').

    Raises:
        getopt.error: If an error occurs during option parsing.

    Examples:
        >>> options = get_options(["-c", "-k", "123"])
        >>> print(options)
        {'caption': 'True', 'db_insert': 'True', 'id': '123'}
    '''
    options = 'cik:'

    long_options = [
        'metadata activity is added as caption below the picture',
        'ignore database - id of the downloaded media is not added to the local db',
        "child id value for the child's profile = "]

    try:
        arguments, _ = getopt.getopt(args, options, long_options)
        inputs = {
            'caption': 'False',
            'db_insert': 'True',
            'id': '0'
        }
        for currentargument, currentvalue in arguments:
            if currentargument in ('-c', '--metadata'):
                inputs['caption'] = 'True'
            elif currentargument in ('-i', '--ignore_db'):
                inputs['db_insert'] = 'False'
            elif currentargument in ('-k', '--id'):
                inputs['id'] = currentvalue
            elif currentargument in ('-h', '--help'):
                print('get help')

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err), type(err))
        usage()

    return inputs


def make_db_file(child_id: str, db_insert: bool) -> None:
    '''
    Creates or checks a database file for a given child ID.

    This function ensures that a database file named id.db exists for a specific
    child ID within a corresponding directory. It creates the directory and file
    if necessary and checks for writability. It also handles potential errors and
    exits the program with an error code if file creation or writing fails.

    Args:
        child_id: The child ID string for which the database file is managed.
        db_insert: A string indicating whether the user wants to update the database
            (value "0"). If not set to "0", the database file is not created or checked.

    Returns:
        None. The function primarily creates and checks file and directory states.

    Raises:
        OSError: If file/directory creation or writing fails.
    '''
    if os.path.exists(f'{os.getcwd()}/{child_id}'):
        if db_insert:  # user wants to update the db, check we can write to it
            if not os.access(f'{os.getcwd()}/{child_id}/id.db', os.W_OK):
                print(f'{os.getcwd()}/{child_id}/id.db exists but is not writable.\
                    Downloaded media will not be added to db')
        try:
            if os.path.isfile(f'{os.getcwd()}/{child_id}/id.db'):
                if not os.access(f'{os.getcwd()}/{child_id}/id.db', os.W_OK):
                    print("The file exists but is not writable.")
            else:
                # Create the file
                with open(f'{os.getcwd()}/{child_id}/id.db', "w", encoding='utf-8') as f:
                    f.write('')
                print("The file was created and is writable.")
        except OSError as oserr:
            print(f'Cannot create db file: {oserr}')
            sys.exit(2)
    else:
        try:
            os.makedirs(f'{os.getcwd()}/{child_id}')
            print(f'{os.getcwd()}/{child_id}')
        except OSError as oserr:
            print(f'Cannot create db folder: {oserr}')
            sys.exit(2)


def get_db_entries(filename: str) -> set[str]:
    '''
    Reads entries from a database file and returns them as a set.

    This function attempts to read all entries from a text-based database file
    specified by the `filename` argument. It opens the file, reads its contents,
    splits them into individual entries, and returns them as a Python set.

    Args:
        filename: The path to the database file (string).

    Returns:
        A set containing the entries found in the database file. If the file
        doesn't exist or is empty, an empty set is returned.

    Raises:
        OSError: If an error occurs while opening or reading the file.

    Examples:
        >>> entries = get_db_entries("my_db.txt")
        >>> print(entries)
        {"entry1", "entry2", "entry3"}
    '''
    try:
        return set(open(filename, encoding='utf-8').read().split())
    except OSError as oserr:
        print(f'OS Error: {oserr}')
        sys.exit(3)


def connect_to_kc(child_id: str, id_set: set[str]) -> dict[str, any]:
    '''
    This function connects to the KinderCare classroom API using the provided child ID,
    fetches media entries, extracts relevant information, and returns a dictionary
    containing the processed data. It uses the `id_set` for comparison and deduplication
    purposes.

    Args:
        child_id: The child ID string used for data retrieval (str).
        id_set: A set of existing media IDs for comparison and deduplication (set[str]).

    Returns:
        A dictionary containing processed media data, with keys and values specific to
        the extracted information (dict[str, any]). The exact structure and meaning of
        the returned data depend on the implementation details of get_kcdata().

    Raises:
        requests.exceptions.RequestException: If an error occurs during API requests.

    See Also:
        - get_kcdata() (function used internally for data processing)
    '''
    count = 1
    new_results = True
    results = {}
    cookies = {'_himama_session': HIMAMA_SESSION_ID}
    while new_results:
        print(f'Getting media from page {count}')
        try:
            req = requests.get(
                f'https://classroom.kindercare.com/accounts/{child_id}/journal_api?page={count}',
                cookies=cookies,
                timeout=30).json()
        except requests.exceptions.RequestException as err:
            print(f'Failed to get data from page {count}. Error: {err}')
        results.update(get_kcdata(req, id_set))
        if len(req['intervals']) == 0:
            new_results = False
            print('All media retrieved')
        count += 1
    return results


def get_kcdata(json_data: dict[str, any], id_set: set[str]) -> dict[str, str]:
    '''
    Processes KinderCare API data to extract media information and filters based on an ID set.

    This function takes a dictionary representing KinderCare API response data (json_data)
    and a set of existing media IDs (id_set) for comparison. It iterates through the
    provided data, extracts relevant information for activities, and builds a dictionary
    containing details for each unique image or video. Activities with IDs already present in
    the id_set are skipped.

    Args:
        json_data: A dictionary containing the parsed JSON response from the KinderCare API 
            (dict[str, any]).
        id_set: A set of existing media IDs used for deduplication (set[str]).

    Returns:
        A dictionary containing processed media data, where keys are unique activity IDs and
        values are dictionaries with extracted information (dict[str, dict[str, str]]). Each inner
        dictionary has the following keys:
            - 'title': The title of the activity (string).
            - 'desc': The description of the activity (string).
            - 'create_date': The date and time the activity was created (string).
            - 'image': The URL of the image associated with the activity (string).
            - 'video': The URL of the video associated with the activity (string, or empty string 
                        if no video exists).

    See Also:
        - connect_to_kc() (function that might use this function internally)
    '''
    media_files = {}
    for _, data in json_data['intervals'].items():
        for item in enumerate(data):
            if f"{item[1]['activity']['id']}" not in id_set:
                # continue
            # else:
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
                media_files[activity_id] = {
                    'title': title,
                    'desc': desc,
                    'create_date': create_date,
                    'image': image,
                    'video': video
                }
    return media_files


def get_images_videos(
        media_info: dict[str, dict[str, str]], id_num: str) -> set[str]:
    '''
    Downloads and saves images and videos from KinderCare API data, updates metadata, and 
    returns downloaded IDs.

    This function iterates through a dictionary containing media information (media_info)
    and extracts image and video URLs. It attempts to download each valid URL, saves the
    content to a file with appropriate naming based on the provided ID and creation date,
    and updates metadata. It also tracks downloaded media IDs in a set and returns it.

    Args:
        media_info: A dictionary containing information about media (dict[str, dict[str, str]]).
            Each inner dictionary has keys like 'title', 'desc', 'image', and 'video'.
        id_num: The child ID string used for directory and file naming (str).

    Returns:
        A set containing the integer IDs of successfully downloaded images and videos (set[int]).

    Raises:
        requests.exceptions.RequestException: If an error occurs during downloads.
    '''
    ids_downloaded = set()
    for activity_id, data in media_info.items():
        if data['image'] is not None:
            date = data['create_date'].replace(':', '_')
            filename = f'{os.getcwd()}/{id_num}/{activity_id}_{date}.jpg'
            try:
                req = requests.get(data['image'], timeout=30)
                req.raise_for_status()
            except requests.exceptions.RequestException as err:
                print(
                    f'unable to get image {
                        data["image"]}: {req.status_code} - {err}')
            open(filename, 'wb').write(req.content)
            # update_exif_data(filename, data)
            ids_downloaded.add(activity_id)

        if data['video'] is not None:
            date = data['create_date'].replace(':', '_')
            filename = f'{os.getcwd()}/{id_num}/{activity_id}_{date}.mov'
            try:
                req = requests.get(data['video'], timeout=30)
                req.raise_for_status()
            except requests.exceptions.RequestException as err:
                print(
                    f'unable to get image {
                        data["image"]}: {req.status_code} - {err}')

            open(filename, 'wb').write(req.content)
            # update_video_data(filename, data)
            ids_downloaded.add(activity_id)
    return ids_downloaded


def update_db_info(child_id: str, activity_id: set[str]) -> None:
    '''
    Updates a local database file with a set of downloaded media IDs.

    This function takes a set of downloaded media IDs (`id_set`) and updates a text-based
    database file located in the child's directory. It reads the existing IDs from the file,
    combines them with the provided `id_set`, and writes the updated set back to the file
    with each ID on a separate line.

    Args:
        child_id: A string ID of the child ID.
        id_set: A set containing string IDs of downloaded media (set[str]).

    Returns:
        None. The function primarily updates the database file.

  Raises:
    IOError: If an error occurs while reading or writing the file.
    OSError: If an error occurs while reading or writing the file.
    '''
    filename = f'{os.getcwd()}/{child_id}/id.db'
    current_db = set(open(filename, encoding='utf-8').read().split())
    current_db.update(activity_id)
    try:
        with open(filename, 'w', encoding='utf-8') as id_db:
            for id_number in current_db:
                id_db.write(f'{id_number}\n')
    except (OSError, IOError) as oserr:
        print(f'Unable to write to id.db file: {oserr}')


def update_exif_data(filename: str, media_info: dict):
    '''
    Updates the exif data on the images downloaded

    Still being worked on as data is not written in a readable format

    '''
    print('Not Implemented Yet...')


def update_video_data(filename: str, media_info: dict):
    '''
    Updates the exif data on the videos downloaded

    Still being worked on as data is not written in a readable format

    '''
    print('Not Implemented Yet...')


getopts = get_options(sys.argv[1:])

make_db_file(getopts['id'], getopts['db_insert'])

db_ids = get_db_entries(f'{os.getcwd()}/{getopts["id"]}/id.db')
kc_web_data = connect_to_kc(getopts['id'], db_ids)
# kc_media = get_kcdata(kc_web_data, db_ids)
# new_ids = get_images_videos(kc_media, getopts['id'])
# update_db_info(new_ids)
new_ids = get_images_videos(kc_web_data, getopts['id'])
update_db_info(getopts['id'], new_ids)
