import yt_dlp as youtube_dl
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def download_youtube_video():
    yt_url = yt_link_entry.get()  # YouTube-Link aus dem Eingabefeld
    try:
        if yt_url:
            # Ordner auswählen, in dem das Video gespeichert werden soll
            output_folder = filedialog.askdirectory(title="Select Output Folder")
            if not output_folder:
                messagebox.showerror("Error", "No output folder selected!")
                return

            # yt-dlp Konfiguration
            ydl_opts = {
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            }

            # Download des Videos
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

            file_label.config(text="Download completed!")
            messagebox.showinfo("Success", "Download completed successfully!")
        else:
            messagebox.showerror("Error", "No YouTube link provided!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while downloading: {e}")

# GUI Setup
root = tk.Tk()
root.title("YouTube Video Downloader")

# YouTube-Link Eingabe
yt_link_label = tk.Label(root, text="YouTube Link:")
yt_link_label.pack(pady=5)
yt_link_entry = tk.Entry(root, width=50)
yt_link_entry.pack(pady=5)

# Button zum Starten des Downloads
download_button = tk.Button(root, text="Download Video", command=download_youtube_video)
download_button.pack(pady=10)

# Label zur Anzeige des Download-Status
file_label = tk.Label(root, text="No file downloaded")
file_label.pack(pady=5)

# Start der Tkinter-GUI
root.mainloop()