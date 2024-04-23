kindercare_sync
===============

Download images and videos with metadata for archiving from the Kindercare website (Himama platform)

Description
-----------

Sync utility for kindercre media. This uses a Local id db (file: id.db) makes sure that you only download the media files you did not download already. 

Thild id is required for downloading media.  To get the child id go to https://classroom.kindercare.accounts. The child ID is in the url in the format: https://classroom.kindercare.com/accounts/xxxxxx 

You will be prompted for your username and password to the Kindercare classroom page.  This is required to get a necessary cookie. This information is not stored or saved anywhere. After you enter your password a Chrome Window will open. It will close on its own.

Requirements:
* Chromedriver.exe (tested with 122.0.6261.128 and Chrome 123). Download at: https://googlechromelabs.github.io/chrome-for-testing/
* exiftool.exe (tested with 12.7.8.0). Download at: https://exiftool.org/

Use
---

kcsync -k ######

	-k : child id value for the child's profile xxxxxx
	(optional flag) -i : ignore db - id of downloaded media is not added to the local db (so media can be downloaded again)
	
This was tested on Python 3.12.2 with the modules in the requirements.txt file.

Known Issues
---
	Metadata is not added videos.

This was based on the shell script from tkuppens located at https://github.com/tkuppens/kindercare
