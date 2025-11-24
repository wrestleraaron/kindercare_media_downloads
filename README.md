# KinderCare(and Lillio-Powered) Media Downloader

![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Last Commit](https://img.shields.io/github/last-commit/wrestleraaron/kindercare_media_downloads)
![Issues](https://img.shields.io/github/issues/wrestleraaron/kindercare_media_downloads)
![Stars](https://img.shields.io/github/stars/wrestleraaron/kindercare_media_downloads?style=social)
![Forks](https://img.shields.io/github/forks/wrestleraaron/kindercare_media_downloads?style=social)


## Overview
This application allows you to download images and videos from your child’s daycare profile — including **KinderCare** (via Himama backend) and other **Lillio-powered childcare centers**.

It uses the **Playwright** browser automation framework to fetch media from these platforms and saves it locally on your computer.  
It also updates **EXIF** and video metadata (title and description) for images and videos.

The tool functions as a *sync utility* — maintaining a local ID database (`id.db`) to only download new media.  
It is confirmed to work with multiple child care centers using Lillio (formerly HiMama), such as Little Discoveries Early Learning Cooperative, Lakeside Childcare, and Little Explorer Montessori.

---

## Requirements
- Python 3.12 recommended (older versions of Python 3 may also work).  
- `exiftool.exe` and `ffmpeg.exe` must be present in the same directory as this program **or** be available in your system’s PATH.

---

## Installation & How to Run

1. **Install requirements**  
   Ensure you have Python 3.12 (or another Python 3 version) installed.
   Then, install the dependencies from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Playwright**
   ```bash
   python -m playwright install
   ```
   
3. **Run the Python script**  
   To start downloading media, run:

   ```bash
   python kc.py
   ```

4. **Optional flag**  
   If you want to ignore the existing database and force a full fresh download:

   ```bash
   python kc.py -i
   ```

> Note: If you have a compiled executable (`kindercare_downloader.exe`), you can also use that as described below:

```bash
kindercare_downloader.exe
kindercare_downloader.exe -i  # optional flag for full refresh
```

---

## Providing Your Child’s ID
You must provide your child’s ID for proper media organization.  
To find it:

1. Log in to the KinderCare Classroom portal.
2. Open the **Manage Children** page:  
   `https://classroom.kindercare.com/accounts`
3. The ID is the number in the URL when viewing your child’s account page, for example:  
   `https://classroom.kindercare.com/accounts/xxxxxx`

---

## Additional Notes
- An internet connection is required to fetch and download media.
- Images are saved as `.jpg`, and videos are saved as `.mov`.
- EXIF metadata for images and video titles/descriptions are automatically updated.

---

## Troubleshooting
- If downloads fail, verify that `ffmpeg.exe` and `exiftool.exe` are in the same directory as the program.
- Errors will print to the console for debugging.
- If media is not downloading, try running with the `-i` flag to rebuild the local database.

---

## License
This project is licensed under the **GPL-3.0 License**.

---

## Contact
For support or suggestions, contact:  
**`yvs9j135@duck.com`**
