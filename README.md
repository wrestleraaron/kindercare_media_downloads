kindercare_sync
===============

Download pictures and videos with metadata for archiving from the Kindercare website (Himama platform)

Windows Easy Button
-----------
* Go to https://tinyurl.com/mvaebp5x and download the executable and helper files.
* Extract the files to your Downloads (or other folder)
* Double-click the file "kindercare_downloader.exe". This will open a command-prompt window (typically with a black background)
* *  This will open a new browser window. Sign into Kindercare as you normally would (you have 5 minutes)
* *   The application will download all photos and videos and put them in folders corresponding to your child's ID number
* *   When the application is finished, the command-prompt window will close and your files will be downloaded.

  ** There is a README.txt file you can reference for additional information

Description
-----------

Sync utility for kindercre media. Local id db (file: id.db) makes sure that you only download the media files you did not download already. 

child id

You need to provide your child's id in the script. See Manage Children page: https://classroom.kindercare.com/accounts . The ID is in the url : https://classroom.kindercare.com/accounts/xxxxxx 


cookie

Cookiefile has to be called cookies.txt and has to be in the same dir as the kcsync script.
Must contain the Netscape-style cookie.  _himama_session (has a long expiration date, so you only need to provide it ones. By the time it expires your little one will be in college)


Use
---

kcsync -ci 

	-i : ignore db - id of downloaded media is not added to the local db
	-c : metadata activity information is added as  caption below the picture.
	-k : child id value for the child's profile xxxxxx


Dependencies
------------

	- jq
	- exiftool
	- ImageMagick (convert)
	- ffmpeg
	- wget
 
