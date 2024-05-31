
# kindercare_media_downloads

Sync utility for kindercare media. This uses a Local id db (file: id.db) makes sure that you only download the media files you did not download already. 

Thild id is required for downloading media.  To get the child id go to https://classroom.kindercare.accounts. The child ID is in the url in the format: https://classroom.kindercare.com/accounts/xxxxxx 

You will be prompted for your username and password to the Kindercare classroom page.  This is required to get a necessary cookie. This information is not stored or saved anywhere. After you enter your password a Chrome Window will open. It will close on its own.



## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)



## Authors

- [@wrestleraaron](https://www.github.com/wrestleraaron)


## Requirements

* Chromedriver.exe - most recent recommended, this waas tested with 122.0.6261.128 and Chrome 123.0.6312.106). 
    * Download at: https://googlechromelabs.github.io/chrome-for-testing/
* exiftool.exe (tested with 12.7.8.0).
    * Download at: https://exiftool.org/
 
Tested on Windows 11 Home 23H2 OS Build 22631.3447 but should work on Windows 10 and Windows 11.
## Run Locally

Clone the project

```bash
  git clone https://github.com/wrestleraaron/kindercare_media_downloads
```

Go to the project directory

```bash
  cd kindercare_media_downloads
```

Optional create a virtual python environment and activate it:

```bash
python -m venv venv
. venv/activate (Unix/Mac)
venv\scripts\activate (Windows)
```

Install dependencies

```bash
  pip install -r requirements.txt
```

via python:
```bash
  python polldaddy_automation.py -k #######
    -k : child id value for the child's profile xxxxxx
	-i : ignore db - id of downloaded media is not added to the local db (so media can be downloaded again) (Optional)

This was tested with Python 3.12.2
```

Run the application as a standalone executable:
```bash
  polldaddy_automation.exe -k #######
    -k : child id value for the child's profile xxxxxx
	-i : ignore db - id of downloaded media is not added to the local db (so media can be downloaded again) (Optional)
```



## Known Issues
Metadata is not added to videos.
## Acknowledgements

 Based on the shell script from [tkuppens](https://github.com/tkuppens/kindercare)
