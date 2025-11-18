'''
Download posted media from your childcare provider (Lillio or Kindercare)
'''
import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Set, Tuple

import ffmpeg
import requests
from playwright.sync_api import sync_playwright

# Location of auth file for saving cookies
AUTH_FILE = Path("auth_state.json")

# Set your provider, either KinderCare or Lillio (Himama)
PROVIDER = "Kindercare"

def usage_help() -> None:
    """Prints usage help and exits the program."""
    print(f'Usage: {sys.argv[0]} [-i]')
    print('Use the -i flag to ignore writing to the local database, allowing the pictures and')
    print('videos to be downloaded again on this device.')
    print(f"Pictures and videos are stored in a folder corresponding to the child's {PROVIDER} ID")
    sys.exit(1)


def get_options(args = sys.argv[1:]) -> dict[str, Any]:
    """
    Parses command-line arguments.

    Args:
        args (list[str]): List of command-line arguments.

    Returns:
        dict[str, Any]: Dictionary with parsed command-line options.
    """
    parser = argparse.ArgumentParser(description=f"Download media from {PROVIDER} accounts.")
    parser.add_argument('-i', '--ignore', action='store_true',
                        help='Do not add media to local database')
    parser.add_argument('-?', dest='need_help', action='store_true',
                        help='Show help message')
    opts = parser.parse_args(args)
    return vars(opts)

def make_db_file(child_id: str) -> None:
    """
    Creates a local database file for a given child ID if it doesn't already exist.

    Args:
        child_id (str): provider's child ID.

    Raises:
        SystemExit: If the file or folder can't be created.
    """
    folder = Path.cwd() / child_id
    db_file = folder / "id.db"

    try:
        folder.mkdir(parents=True, exist_ok=True)
        if not db_file.exists():
            db_file.write_text('', encoding='utf-8')
            print(f"Created database file: {db_file}")
    except OSError as err:
        print(f'Cannot create db file: {err}. Please create this folder')
        sys.exit(2)


def get_db_entries(filename: str) -> Set[str]:
    """
    Reads a database file and returns the set of activity IDs.

    Args:
        filename (str): Path to the database file.

    Returns:
        Set[str]: Set of stored activity IDs.

    Raises:
        SystemExit: If the file can't be read.
    """
    try:
        return set(Path(filename).read_text(encoding='utf-8').split())
    except OSError as err:
        print(f'OS Error: {err}')
        sys.exit(3)


def connect_to_kc_playwright(WEB_URL: str, context, child_id: str, id_set: Set[str]) -> Dict[str, Any]:
    """
    Retrieves all media metadata from provider using the Playwright context.

    Args:
        context: Playwright context.
        child_id (str): provider's child ID.
        id_set (Set[str]): Set of already downloaded activity IDs.

    Returns:
        Dict[str, Any]: Dictionary of media metadata keyed by activity ID.
    """
    count = 1
    results = {}

    while True:
        print(f'Getting media from page {count}')
        url = f'https://{WEB_URL}/accounts/{child_id}/journal_api?page={count}'
        try:
            response = context.request.get(url)
            data = response.json()
        except Exception as err:
            print(f'Failed to get data from page {count}. Error: {err}')
            break

        results.update(get_kcdata(data, id_set))
        if not data.get('intervals'):
            print('All media retrieved.\nDownloading files...')
            break
        count += 1

    return results


def get_kcdata(json_data: Dict[str, Any], id_set: Set[str]) -> Dict[str, Dict[str, str]]:
    """
    Filters provider's media JSON for new entries.

    Args:
        json_data (Dict[str, Any]): Parsed JSON response from provider.
        id_set (Set[str]): Set of previously downloaded activity IDs.

    Returns:
        Dict[str, Dict[str, str]]: Filtered media metadata.
    """
    media_files = {}
    for _, data in json_data.get('intervals', {}).items():
        for item in data:
            activity_id = str(item['activity']['id'])
            if activity_id not in id_set:
                title = item['activity'].get('title') or "Look what I'm doing today!"
                desc = item['activity'].get('description') or title
                create_date = item['activity']['created_at'].split('.', 1)[0]
                image = item['activity'].get('image', {}).get('big', {}).get('url')
                video = item['activity'].get('video', {}).get('url')

                media_files[activity_id] = {
                    'title': title,
                    'desc': desc,
                    'create_date': create_date,
                    'image': image,
                    'video': video or ''
                }
    return media_files


def get_images_videos(media_info: Dict[str, Dict[str, str]], id_num: str) -> Set[str]:
    """
    Downloads images and videos for a given child profile.

    Args:
        media_info (Dict[str, Dict[str, str]]): Metadata of media to download.
        id_num (str): provider's child ID.

    Returns:
        Set[str]: Set of successfully downloaded activity IDs.
    """
    ids_downloaded = set()
    folder = Path.cwd() / id_num
    print(f"Downloading {len(media_info)} pictures and videos...")

    for idx, (activity_id, data) in enumerate(media_info.items(), 1):
        if idx % 10 == 0:
            print(f"Processed {idx} media items...", flush=True)
        date_str = data['create_date'].replace(':', '_')
        if data['image']:
            image_path = folder / f"{activity_id}_{date_str}.jpg"
            try:
                response = requests.get(data['image'], timeout=30)
                response.raise_for_status()
                image_path.write_bytes(response.content)
                update_exif_data(image_path, data)
                update_datestamp(image_path, data['create_date'])
                ids_downloaded.add(activity_id)
            except requests.exceptions.RequestException as err:
                print(f'Failed to download image: {err}')

        if data['video']:
            video_path = folder / f"{activity_id}_{date_str}.mov"
            try:
                response = requests.get(data['video'], timeout=30)
                response.raise_for_status()
                video_path.write_bytes(response.content)
                update_datestamp(video_path, data['create_date'])
                ids_downloaded.add(activity_id)
            except requests.exceptions.RequestException as err:
                print(f'Failed to download video: {err}')

    return ids_downloaded


def update_db_info(child_id: str, activity_ids: Set[str]) -> None:
    """
    Updates the database file with new activity IDs.

    Args:
        child_id (str): provider's child ID.
        activity_ids (Set[str]): Set of new activity IDs.

    Raises:
        OSError: If unable to write to the file.
    """
    db_file = Path.cwd() / child_id / "id.db"
    try:
        current_entries = get_db_entries(str(db_file))
        updated_entries = current_entries.union(activity_ids)
        db_file.write_text('\n'.join(updated_entries), encoding='utf-8')
    except (OSError, IOError) as err:
        print(f'Unable to write to db file: {err}')


def encode_utf16le_hex(text: str) -> str:
    """
    Encodes a string to UTF-16LE and returns it as a hex string.

    Returns:
        str: A hexadecimal string representing the UTF-16LE encoded input passed as text.

    """
    return ''.join(f'{b:02x}' for b in text.encode('utf-16le')) + '0000'


def update_exif_data(filename: Path, media_info: Dict[str, str]) -> None:
    """
    Updates EXIF metadata on a given image file using ExifTool.

    Args:
        filename (Path): Path to the image file.
        media_info (Dict[str, str]): Metadata with title, description, and date.

    Raises:
        subprocess.CalledProcessError: If ExifTool fails.
    """
    title = media_info['title']
    comment = media_info['desc']
    orig_date = datetime.strptime(media_info['create_date'], '%Y-%m-%dT%H:%M:%S')

    exiftool_path = get_tool_path('exiftool.exe')
    args = [
        exiftool_path,
        f'-xptitle#={encode_utf16le_hex(title)}',
        f'-xpcomment#={encode_utf16le_hex(comment)}',
        f'-datetimeoriginal={orig_date}',
        '-q',
        str(filename)
    ]

    try:
        subprocess.check_call(args)
        original_file = filename.with_name(filename.name + '_original')
        if original_file.exists():
            original_file.unlink()
    except subprocess.CalledProcessError as err:
        print(f"ExifTool failed: {err}")


def update_datestamp(file: str, datestamp: str):
    '''
    Updates the datestamp of the file to match the date the media was taken.

    Args:
        file: The path to the image file (str).
        datestamp: The creation date of the media in YYYY-MM-DDTHH:MM:SS format. (str)

    Raises:
        Exception: If the timestamp cannot be updated. Not fatal error.
    '''
    dt = datetime.strptime(datestamp, "%Y-%m-%dT%H:%M:%S")
    dt_num = int(dt.timestamp())
    try:
        os.utime(file, (dt_num, dt_num))
    except Exception as err:
        print(f'Unable to update timestamp of {file} ({err})')


def update_video_data(filename: Path, media_info: Dict[str, str]) -> None:
    """
    Updates video metadata (title and comment) using ffmpeg.

    Args:
        filename (Path): Path to the video file.
        media_info (Dict[str, str]): Metadata with title and description.

    Raises:
        ffmpeg.Error: If ffmpeg encounters an error.
    """
    title = media_info.get('title', 'No Title')
    comment = media_info.get('desc', 'No Description')
    ffmpeg_path = get_tool_path('ffmpeg.exe')

    try:
        (
            ffmpeg.input(str(filename))
            .output(str(filename), metadata=f'title={title}', **{'metadata:g': f'comment={comment}'})
            .global_args('-y')
            .run(cmd=ffmpeg_path)
        )
        print(f"Video metadata updated: {filename}")

    except ffmpeg.Error as e:
        print(f"Failed to update video metadata: {e}")


def signme_in(signin_url: str) -> Tuple[Any, Set[str], Any, Any]:
    """
    Automates browser sign-in using Playwright.

    Args:
        signin_url (str): URL for provider sign-in.

    Returns:
        Tuple[Any, Set[str], Any, Any]: Context, set of profile IDs, browser, 
        and playwright instance.
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)

    if AUTH_FILE.exists():
        context = browser.new_context(storage_state=str(AUTH_FILE))
    else:
        context = browser.new_context()

    page = context.new_page()

    page.goto(signin_url)
    page.wait_for_function(f'document.location.href !== "{signin_url}"', timeout=300000)

    page.goto(f"{signin_url}/accounts")
    page.wait_for_selector('a:has-text("Profile")', timeout=300000)
    profile_links = page.query_selector_all('a:has-text("Profile")')

    page.context.storage_state(path=str(AUTH_FILE))

    account_numbers = {
        match.group(1)
        for link in profile_links
        if (href := link.get_attribute('href')) and (match := re.search(r'/accounts/(\d+)', href))
    }

    page.close()
    return context, account_numbers, browser, p


def get_tool_path(tool_name: str) -> str:
    """
    Resolves the correct path to a tool executable, depending on whether the script is running
    in a bundled environment or as a regular script.

    Args:
        tool_name (str): The filename of the tool executable (e.g., 'ffmpeg.exe').

    Returns:
        str: Absolute path to the tool executable.
    """
    if getattr(sys, 'frozen', False):
        return str(Path(sys._MEIPASS) / 'tools' / tool_name)
    else:
        return str(Path('tools') / tool_name)


def main(ignore: bool, need_help: bool) -> None:
    """
    Main control flow for the media downloader.

    Args:
        ignore (bool): Whether to skip updating the local database.
        need_help (bool): Whether to display the usage help.
    """
    if need_help:
        usage_help()

    # Set URL based on PROVIDER value
    if PROVIDER.lower() == "kindercare":
        WEB_URL = "classroom.kindercare.com"
    elif PROVIDER.lower() == "lillio":
        WEB_URL = "himama.com"
    else:
        raise ValueError(f"Unsupported provider: {PROVIDER}. Supported: 'Kindercare', 'Lillio'")

    context, profile_ids, browser, playwright = signme_in(f'https://{WEB_URL}')

    for profile_id in profile_ids:
        print(f'Getting data for {profile_id}...')
        if not ignore:
            make_db_file(profile_id)

        db_ids = get_db_entries(str(Path.cwd() / profile_id / "id.db"))
        kc_web_data = connect_to_kc_playwright(WEB_URL, context, profile_id, db_ids)
        new_ids = get_images_videos(kc_web_data, profile_id)

        if not ignore:
            update_db_info(profile_id, new_ids)
        print(f"All photos and videos downloaded for {profile_id}.")
    browser.close()
    playwright.stop()



if __name__ == '__main__':
    options = get_options()
    main(**options)

