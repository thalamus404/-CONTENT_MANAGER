import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from moviepy.editor import VideoFileClip
import random
import os
from pytube import YouTube
import webbrowser

# Globale Variable für den Downloads-Ordner-Pfad
downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

def download_youtube_video():
    global video_file
    try:
        yt_url = yt_link_entry.get()
        if yt_url:
            yt = YouTube(yt_url)
            video_stream = yt.streams.filter(file_extension='mp4', res="720p").first()
            video_file = video_stream.download()
            file_label.config(text=f"Downloaded: {os.path.basename(video_file)}")
        else:
            messagebox.showerror("Error", "No YouTube link provided!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while downloading: {e}")

def select_file():
    global video_file
    video_file = filedialog.askopenfilename(title="Select a video file", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    if video_file:
        file_label.config(text=f"Selected file: {os.path.basename(video_file)}")

def open_downloads_folder():
    webbrowser.open(downloads_folder)

def generate_clips():
    try:
        # Lade das Video
        video = VideoFileClip(video_file)
        video_duration = int(video.duration)

        # Anzahl Clips und Länge pro Clip
        num_clips = int(num_clips_entry.get())
        clip_length = int(clip_length_entry.get())

        # Ordnername für Speicherung im Downloads-Folder
        folder_name = folder_name_entry.get()
        output_folder = os.path.join(downloads_folder, folder_name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Clip Namen
        base_name = name_entry.get()

        # Fortschrittsleiste zurücksetzen
        progress_bar["value"] = 0
        progress_bar["maximum"] = num_clips

        # Zeitpunkte auslesen oder zufällig erstellen
        timecodes = []
        if random_choice.get():
            for _ in range(num_clips):
                start_time = random.randint(0, video_duration - clip_length)
                timecodes.append(start_time)
        else:
            timecode_str = timecodes_entry.get()
            timecodes = [int(tc.strip()) for tc in timecode_str.split(",") if tc.strip().isdigit()]

        # Clips generieren
        for i, start_time in enumerate(timecodes):
            clip = video.subclip(start_time, start_time + clip_length)

            # Zentrale Berechnung: Vertikales Format (1080x1920) zentrieren
            center_x = clip.w / 2  # Center des 16:9-Bildes berechnen
            vertical_clip = clip.crop(x_center=center_x, width=1080, height=1920)

            # Wichtig: Video auch auf die vertikale Auflösung bringen
            vertical_clip = vertical_clip.resize(newsize=(1080, 1920))

            output_filename = f"{base_name}_{i + 1}.mp4" if base_name else f"clip_{i + 1}.mp4"
            output_path = os.path.join(output_folder, output_filename)
            vertical_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

            # Fortschrittsleiste und Log-Feedback aktualisieren
            progress_bar["value"] += 1
            root.update_idletasks()
            log_output.insert(tk.END, f"Video {i + 1} von {num_clips} fertiggestellt: {output_filename}\n")
            log_output.see(tk.END)

        messagebox.showinfo("Success", "All clips generated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# GUI Setup
root = tk.Tk()
root.title("YouTube Video Clip Generator")

# YouTube Link Eingabe
yt_link_label = tk.Label(root, text="YouTube Link:")
yt_link_label.pack(pady=5)
yt_link_entry = tk.Entry(root, width=50)
yt_link_entry.pack(pady=5)

# YouTube Download Button
yt_download_button = tk.Button(root, text="Download YouTube Video", command=download_youtube_video)
yt_download_button.pack(pady=10)

# Alternativ: Datei lokal auswählen
file_button = tk.Button(root, text="Select Video File", command=select_file)
file_button.pack(pady=10)
file_label = tk.Label(root, text="No file selected")
file_label.pack(pady=5)

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

# Ordnername für Speicherort
folder_name_label = tk.Label(root, text="Folder Name (in Downloads):")
folder_name_label.pack(pady=5)
folder_name_entry = tk.Entry(root)
folder_name_entry.pack(pady=5)

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

# Fortschrittsleiste
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Log-Output für Fortschritt
log_output = tk.Text(root, height=10, width=60)
log_output.pack(pady=10)

# Button zum Erstellen der Clips
generate_button = tk.Button(root, text="Generate Clips", command=generate_clips)
generate_button.pack(pady=20)

# Button zum Öffnen des Downloads-Ordners
open_folder_button = tk.Button(root, text="Open Downloads Folder", command=open_downloads_folder)
open_folder_button.pack(pady=10)

root.mainloop()