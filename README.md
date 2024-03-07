kindercare_sync
===============

Download images and videos with metadata for archiving from the Kindercare website (Himama platform)

Description
-----------

Sync utility for kindercre media. This uses a Local id db (file: id.db) makes sure that you only download the media files you did not download already. 

Thild id is required for downloading media.  To get the child id go to https://classroom.kindercare.accounts. The child ID is in the url in the format: https://classroom.kindercare.com/accounts/xxxxxx 

The Himama session ID is required.  The easiest way to get this is as follows:
* Click the journal tab after logging in (url is similar to: https://classroom.kindercare.com/accounts/xxxxx/journal)
* Right-click on the page and choose "Inspect"
* Click the network tab and reload the page
* Look for the Name "journal" and Click on Headers
* Look for the Request Header named Cookie and grab the characters after "_himama_session" and in line 15 as the value for "HIMAMA_SESSION_ID"

Use
---

kcsync -ik ######

	-i : ignore db - id of downloaded media is not added to the local db (so media can be downloaded again)
	-k : child id value for the child's profile xxxxxx


This was tested on Python 3.11 with the modules in the requirements.txt file.

Known Issues
---
	Exif data and metadata are not added to images or videos.

This was based on the shell script from tkuppens located at https://github.com/tkuppens/kindercare
