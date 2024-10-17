import os
import pickle
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# API credentials
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Feste Tags (auf 500 Zeichen beschränkt)
TAGS = ["Liam Gallagher", "Oasis", "Britpop", "Rock music", "Manchester", "Supersonic", "Definitely Maybe", 
        "Wonderwall", "Don’t Look Back in Anger", "Beady Eye", "Noel Gallagher", "Gallagher brothers", "Live Forever",
        "Morning Glory", "Oasis reunion", "Cigarettes & Alcohol", "Rock ‘n’ Roll Star", "Liam solo career", "As You Were", 
        "Why Me? Why Not", "Liam Gallagher fashion", "Parka", "Sunglasses", "Britpop revival", "Glastonbury", 
        "Oasis documentary", "Champagne Supernova", "90s rock", "Live gigs", "Manchester music scene", "Knebworth concerts"]

# Funktion zum Hochladen eines Videos
def upload_video(youtube, video_path, video_title):
    request_body = {
        "snippet": {
            "title": video_title,
            "description": "Beschreibung des Videos.",
            "tags": TAGS,
            "categoryId": "22"  # Kategorie: People & Blogs
        },
        "status": {
            "privacyStatus": "public"  # Video öffentlich machen
        }
    }

    # Video hochladen
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

# Funktion zur Authentifizierung
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

# Funktion zum Auswählen und Hochladen der Videos
def upload_videos():
    youtube = authenticate_youtube()
    for i, video_file in enumerate(video_files):
        video_title = title_entries[i].get()  # Titel aus dem Eingabefeld
        print(f"Uploading: {video_title}")
        video_id = upload_video(youtube, video_file, video_title)
        print(f"Uploaded {video_title} (ID: {video_id})")
        log_output.insert(tk.END, f"{video_title} hochgeladen (ID: {video_id})\n")
    messagebox.showinfo("Success", "All videos uploaded successfully!")

# Funktion zum Auswählen der Videos
def select_videos():
    global video_files, title_entries
    video_files = filedialog.askopenfilenames(title="Select Video Files", filetypes=[("MP4 files", "*.mp4")])

    if video_files:
        # Lösche vorherige Einträge
        for widget in title_frame.winfo_children():
            widget.destroy()

        title_entries = []
        for video_file in video_files:
            filename = os.path.basename(video_file)
            label = tk.Label(title_frame, text=filename)
            label.pack(anchor="w")

            entry = tk.Entry(title_frame, width=50)
            entry.insert(0, filename)  # Standardname ist der Dateiname
            entry.pack(anchor="w", padx=10, pady=5)
            title_entries.append(entry)

# GUI Setup
root = tk.Tk()
root.title("YouTube Video Uploader")
root.geometry("600x500")

# Videos auswählen Button
select_button = tk.Button(root, text="Select Videos", command=select_videos)
select_button.pack(pady=10)

# Frame für Video-Titel
title_frame = tk.Frame(root)
title_frame.pack(fill="both", expand=True)

# Fortschrittsleiste
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Log-Output für Fortschritt
log_output = tk.Text(root, height=10, width=60)
log_output.pack(pady=10)

# Upload Button
upload_button = tk.Button(root, text="Upload Videos", command=upload_videos)
upload_button.pack(pady=20)

root.mainloop()