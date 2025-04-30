Kindercare Media Downloader
===========================

Overview:
This application allows you to download images and videos from your child’s KinderCare profile.
It uses the Playwright browser automation framework to fetch media from the KinderCare platform and saves it locally on your computer.
It also updates EXIF and video metadata (title and description) for images and videos.

Requirements:
1. Python 3.x installed on your machine.
2. 'exiftool.exe' and 'ffmpeg.exe' must be present in the same directory as this program or be available in the system’s PATH.

How to Use:
1. Download and extract the contents to a directory.
2. Run the application with the following command:
   - Open Command Prompt in the directory containing the program and type:

     kindercare_downloader.exe

   - Optionally, use the '-i' flag to ignore the database update and force a fresh download of the media again:

     kindercare_downloader.exe -i

3. The program will prompt you to log in to your KinderCare account. After login, it will start downloading your child’s media.
   - Media will be stored in folders named by your child’s KinderCare ID.
   - A local database will track the downloaded media to prevent re-downloads.

Additional Notes:
- The application requires an internet connection for fetching data and downloading media.
- Media files will be saved as '.jpg' for images and '.mov' for videos.
- EXIF metadata for images and video comments/titles are updated.

Troubleshooting:
- If you encounter issues with downloading media, ensure that 'ffmpeg.exe' and 'exiftool.exe' are present in the same folder as the program.
- If any errors occur during the media download, the program will print error messages to the screen for troubleshooting.

License:
This project is licensed under the GPL-3.0 License.

Contact:
For support or suggestions, please contact Aaron Tatone at yvs9j135@duck.com