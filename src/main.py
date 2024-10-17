import os
import pickle
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import yt_dlp as youtube_dl
from tkinter import filedialog, messagebox, ttk
import tkinter as tk
import random
from moviepy.editor import VideoFileClip

# API credentials
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Globale Variable für den Downloads-Ordner
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
video_file = None

# Feste YouTube-Tags
TAGS = ["#shorts", "#oasis"]

### Abschnitt 1: YouTube Downloader ###

def download_youtube_video():
    yt_url = yt_link_entry.get()
    folder_name = folder_name_entry.get()
    
    try:
        if yt_url and folder_name:
            # Erstelle den Hauptordner im Downloads-Verzeichnis
            output_folder = os.path.join(downloads_folder, folder_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Erstelle den "Best"-Ordner im Hauptordner
            best_folder = os.path.join(output_folder, 'Best')
            if not os.path.exists(best_folder):
                os.makedirs(best_folder)

            # yt-dlp Konfiguration
            ydl_opts = {
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            }

            # Download des Videos
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            file_label.config(text=f"Download completed! Video saved in: {output_folder}")
            messagebox.showinfo("Success", f"Download completed successfully! Video saved in: {output_folder}")
        else:
            messagebox.showerror("Error", "No YouTube link or folder name provided!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while downloading: {e}")

### Abschnitt 2: Video Clip Shortener ###

def generate_clips():
    global video_file
    folder_name = folder_name_entry.get()
    if not folder_name:
        messagebox.showerror("Error", "Please enter a folder name first.")
        return

    # Finde das heruntergeladene Video im Ordner
    output_folder = os.path.join(downloads_folder, folder_name)
    video_files = [f for f in os.listdir(output_folder) if f.endswith('.mp4')]
    
    if len(video_files) == 1:
        video_file = os.path.join(output_folder, video_files[0])  # Nimm das heruntergeladene Video
    else:
        messagebox.showerror("Error", "No video file found or multiple video files found.")
        return

    try:
        video = VideoFileClip(video_file)
        video_duration = int(video.duration)

        num_clips = int(num_clips_entry.get())
        clip_length = int(clip_length_entry.get())
        base_name = name_entry.get()

        progress_bar["value"] = 0
        progress_bar["maximum"] = num_clips

        timecodes = []
        if random_choice.get():
            for _ in range(num_clips):
                start_time = random.randint(0, video_duration - clip_length)
                timecodes.append(start_time)
        else:
            timecode_str = timecodes_entry.get()
            timecodes = [int(tc.strip()) for tc in timecode_str.split(",") if tc.strip().isdigit()]

        for i, start_time in enumerate(timecodes):
            clip = video.subclip(start_time, start_time + clip_length)
            center_x = clip.w / 2
            vertical_clip = clip.crop(x_center=center_x, width=1080, height=1920).resize(newsize=(1080, 1920))

            output_filename = f"{base_name}_{i + 1}.mp4" if base_name else f"clip_{i + 1}.mp4"
            output_path = os.path.join(output_folder, output_filename)
            vertical_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

            progress_bar["value"] += 1
            root.update_idletasks()
            log_output.insert(tk.END, f"Video {i + 1} von {num_clips} fertiggestellt: {output_filename}\n")
            log_output.see(tk.END)

        messagebox.showinfo("Success", "All clips generated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

### Abschnitt 3: YouTube Uploader ###

def authenticate_youtube():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def upload_video(youtube, video_path, video_title):
    request_body = {
        "snippet": {
            "title": f"{video_title} #shorts #oasis",
            "description": "Beschreibung des Videos.",
            "tags": TAGS,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress_bar['value'] = int(status.progress() * 100)
            root.update_idletasks()
    return response['id']

def upload_videos():
    youtube = authenticate_youtube()
    folder_name = folder_name_entry.get()

    if not folder_name:
        messagebox.showerror("Error", "Please enter a folder name first.")
        return

    best_folder = os.path.join(downloads_folder, folder_name, "Best")
    video_files = [os.path.join(best_folder, f) for f in os.listdir(best_folder) if f.endswith('.mp4')]

    if not video_files:
        messagebox.showerror("Error", "No videos found in the Best folder.")
        return

    title_entries = []
    for video_file in video_files:
        filename = os.path.basename(video_file)
        title = os.path.splitext(filename)[0]
        title_entries.append(title)

    for i, video_file in enumerate(video_files):
        video_title = title_entries[i]
        video_id = upload_video(youtube, video_file, video_title)
        log_output.insert(tk.END, f"{video_title} hochgeladen (ID: {video_id})\n")
    
    messagebox.showinfo("Success", "All videos uploaded successfully!")

### Gesamte GUI Struktur ###

root = tk.Tk()
root.title("YouTube Video Downloader, Shortener & Uploader")
root.geometry("700x600")

# Frame für YouTube Downloader
yt_link_label = tk.Label(root, text="YouTube Link:")
yt_link_label.pack(pady=5)
yt_link_entry = tk.Entry(root, width=50)
yt_link_entry.pack(pady=5)

folder_name_label = tk.Label(root, text="Folder Name:")
folder_name_label.pack(pady=5)
folder_name_entry = tk.Entry(root, width=50)
folder_name_entry.pack(pady=5)

download_button = tk.Button(root, text="Download Video", command=download_youtube_video)
download_button.pack(pady=10)

file_label = tk.Label(root, text="No file downloaded")
file_label.pack(pady=5)

# Frame für den Video Shortener
# Anzahl der Clips
num_clips_label = tk.Label(root, text="Number of Clips:")
num_clips_label.pack(pady=5)
num_clips_entry = tk.Entry(root)
num_clips_entry.pack(pady=5)

# Länge der Clips
clip_length_label = tk.Label(root, text="Clip Length (seconds):")
clip_length_label.pack(pady=5)
clip_length_entry = tk.Entry(root)
clip_length_entry.pack(pady=5)

# Timecodes manuell eingeben oder zufällig auswählen
timecodes_label = tk.Label(root, text="Enter Timecodes (comma-separated) or choose random:")
timecodes_label.pack(pady=5)
timecodes_entry = tk.Entry(root)
timecodes_entry.pack(pady=5)

random_choice = tk.BooleanVar()
random_checkbox = tk.Checkbutton(root, text="Random Timecodes", variable=random_choice)
random_checkbox.pack(pady=5)

# Namen für die Clips
name_label = tk.Label(root, text="Base Name for Clips:")
name_label.pack(pady=5)
name_entry = tk.Entry(root)
name_entry.pack(pady=5)

generate_button = tk.Button(root,

 text="Generate Clips", command=generate_clips)
generate_button.pack(pady=20)

# Fortschrittsleiste
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Log-Output für Fortschritt
log_output = tk.Text(root, height=10, width=60)
log_output.pack(pady=10)

# Frame für den YouTube Uploader
upload_button = tk.Button(root, text="Upload Videos", command=upload_videos)
upload_button.pack(pady=20)

root.mainloop()