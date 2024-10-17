# YouTube Content Manager

## Description

The **YouTube Content Manager** is an application that downloads YouTube videos, splits them into short clips, and uploads these clips to YouTube. The app utilizes the YouTube API for managing videos and MoviePy to convert videos into vertical formats for Shorts.

## Features

1. **YouTube Video Downloader**: Download YouTube videos and save them to a predefined folder.
2. **Video Clip Shortener**: Create short clips from a downloaded video with a selectable number of clips and clip length.
3. **YouTube Uploader**: Upload selected clips directly to YouTube and automatically add hashtags.

## Requirements

- Python 3.x
- Google API credentials (`client_secret.json`) to access the YouTube API
- Required Python libraries:
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `google-api-python-client`
  - `yt_dlp`
  - `moviepy`
  - `tkinter`

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repository.git
   cd your-repository

2.	**Run Setup**
    ```bash
    bash setup.sh

3.	First Run
On the first run, you will need to configure the application. Run the app in the terminal:
	•	`Select the folder where you want to save videos.`
	•	`Select your client_secret.json to connect with the YouTube API.`

Usage

1. Download YouTube Video

	•	`Enter the URL of the YouTube video in the YouTube Link field.`
	•	`Enter the name of the folder where the video will be saved.`
	•	`Click Download Video to download the video.`

2. Generate Clips

	•	`Choose the number of clips and the clip length.`
	•	`Optionally, enter manual timecodes or choose to generate random clips.`
	•	`Click Generate Clips to create the clips.`

3. Upload Videos to YouTube

	•	`Move the created clips you want to upload into the automatically generated “Best” folder.`
	•	`Click Upload Videos to upload the videos. You will be prompted to enter titles, and the hashtags #shorts #oasis will automatically be added.`

Configuration

The configuration is saved in the config.json file after setup is completed. This file contains:

	•	The path to the downloads folder
	•	The path to the client_secret.json file for the YouTube API

If you want to change the configuration, you can run the setup again.

Notes on the YouTube API

Make sure you are registered with the YouTube API and have your client_secret.json file. This is required to access the YouTube API.

Known Issues

	•	Quota Limit: The YouTube API has daily usage limits. Ensure you don’t exceed your quota to avoid upload errors.
	•	Token Management: A token is stored locally to prevent needing to log in to the YouTube API every time. If it expires, the token will be refreshed automatically.


