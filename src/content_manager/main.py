import os
import pickle
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import yt_dlp
from moviepy.editor import VideoFileClip
import random
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow  # Corrected import
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

class YouTubeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Video Downloader, Shortener & Uploader")
        self.root.state('zoomed')  # Maximize the window
        self.config = {}
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.TAGS = []  # Initialize with empty tags list
        self.setup_ui()
        self.check_for_setup()
        self.root.mainloop()

    def setup_ui(self):
        # YouTube Downloader Frame
        yt_frame = tk.LabelFrame(self.root, text="YouTube Downloader", font=("Arial", 14))
        yt_frame.pack(pady=10, padx=10, fill="x")

        self.yt_link_label = tk.Label(yt_frame, text="YouTube Link:")
        self.yt_link_label.pack(pady=5)
        self.yt_link_entry = tk.Entry(yt_frame, width=50)
        self.yt_link_entry.pack(pady=5)

        self.folder_name_label = tk.Label(yt_frame, text="Folder Name:")
        self.folder_name_label.pack(pady=5)
        self.folder_name_entry = tk.Entry(yt_frame, width=50)
        self.folder_name_entry.pack(pady=5)

        self.download_button = tk.Button(yt_frame, text="Download Video", command=self.download_video_thread)
        self.download_button.pack(pady=10)

        self.download_progress = ttk.Progressbar(yt_frame, orient="horizontal", length=400, mode="determinate")
        self.download_progress.pack(pady=5)

        self.file_label = tk.Label(yt_frame, text="No file downloaded")
        self.file_label.pack(pady=5)

        # Video Shortener Frame
        shortener_frame = tk.LabelFrame(self.root, text="Video Shortener", font=("Arial", 14))
        shortener_frame.pack(pady=10, padx=10, fill="x")

        self.num_clips_label = tk.Label(shortener_frame, text="Number of Clips:")
        self.num_clips_label.pack(pady=5)
        self.num_clips_entry = tk.Entry(shortener_frame)
        self.num_clips_entry.pack(pady=5)

        self.clip_length_label = tk.Label(shortener_frame, text="Clip Length (seconds):")
        self.clip_length_label.pack(pady=5)
        self.clip_length_entry = tk.Entry(shortener_frame)
        self.clip_length_entry.insert(0, "15")  # Default clip length
        self.clip_length_entry.pack(pady=5)

        self.timecodes_label = tk.Label(shortener_frame, text="Enter Timecodes (comma-separated) or choose random:")
        self.timecodes_label.pack(pady=5)
        self.timecodes_entry = tk.Entry(shortener_frame)
        self.timecodes_entry.insert(0, "0,30,60")  # Default timecodes
        self.timecodes_entry.config(state='disabled')  # Disabled by default
        self.timecodes_entry.pack(pady=5)

        self.random_choice = tk.BooleanVar(value=True)
        self.random_checkbox = tk.Checkbutton(shortener_frame, text="Random Timecodes", variable=self.random_choice, command=self.toggle_timecodes_entry)
        self.random_checkbox.pack(pady=5)

        self.name_label = tk.Label(shortener_frame, text="Base Name for Clips:")
        self.name_label.config(font=("Arial", 10))
        self.name_label.pack(pady=5)
        self.name_entry = tk.Entry(shortener_frame)
        self.name_entry.insert(0, "clip")
        self.name_entry.pack(pady=5)

        self.generate_button = tk.Button(shortener_frame, text="Generate Clips", command=self.generate_clips_thread)
        self.generate_button.config(font=("Arial", 10))
        self.generate_button.pack(pady=10)

        self.clip_progress = ttk.Progressbar(shortener_frame, orient="horizontal", length=400, mode='determinate')
        self.clip_progress.pack(pady=5)

        # Log Output
        self.log_output = tk.Text(self.root, height=10, width=60)
        self.log_output.config(state='disabled')
        self.log_output.pack(pady=10)

        # YouTube Uploader Frame
        uploader_frame = tk.LabelFrame(self.root, text="YouTube Uploader", font=("Arial", 14))
        uploader_frame.pack(pady=10, padx=10, fill="x")

        self.tags_label = tk.Label(uploader_frame, text="Tags (comma-separated):")
        self.tags_label.pack(pady=5)
        self.tags_entry = tk.Entry(uploader_frame)
        self.tags_entry.insert(0, "#shorts,#example")
        self.tags_entry.pack(pady=5)

        self.upload_button = tk.Button(uploader_frame, text="Upload Videos", command=self.upload_videos_thread)
        self.upload_button.config(font=("Arial", 10))
        self.upload_button.pack(pady=10)

        self.upload_progress = ttk.Progressbar(uploader_frame, orient="horizontal", length=400, mode='determinate')
        self.upload_progress.pack(pady=5)

        # Tutorial Button
        self.tutorial_button = tk.Button(self.root, text="Show Tutorial", command=self.tutorial_window)
        self.tutorial_button.config(font=("Arial", 10))
        self.tutorial_button.pack(pady=10)

    def toggle_timecodes_entry(self):
        if self.random_choice.get():
            self.timecodes_entry.config(state='disabled')
        else:
            self.timecodes_entry.config(state='normal')

    def check_for_setup(self):
        self.load_config()
        if 'downloads_folder' not in self.config or 'client_secret_file' not in self.config:
            self.run_setup()


    def run_setup(self):
        messagebox.showinfo("Setup", "Please select the folder where you want to save downloads and clips.")
        download_folder = filedialog.askdirectory(title="Select Downloads Folder")
        if not download_folder:
            messagebox.showerror("Error", "No folder selected. Setup aborted.")
            return
        self.config['downloads_folder'] = download_folder

        messagebox.showinfo("Setup", "Please select your client_secret.json file for Google API authentication.")
        client_secret_path = filedialog.askopenfilename(title="Select client_secret.json", filetypes=[("JSON files", "*.json")])
        if not client_secret_path:
            messagebox.showerror("Error", "No client_secret.json file selected. Setup aborted.")
            return
        self.config['client_secret_file'] = client_secret_path

        # Save the configuration
        with open('config.json', 'w') as config_file:
            json.dump(self.config, config_file)
        messagebox.showinfo("Setup", "Setup completed successfully! You can now use the app.")
        self.load_config()  # Reload config after setup

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
        else:
            self.config = {}

    def download_video_thread(self):
        threading.Thread(target=self.download_youtube_video).start()

    def download_youtube_video(self):
        if not self.config:
            messagebox.showerror("Error", "Please run the setup first.")
            return

        yt_url = self.yt_link_entry.get()
        folder_name = self.folder_name_entry.get()

        if yt_url and folder_name:
            output_folder = os.path.join(self.config['downloads_folder'], folder_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            best_folder = os.path.join(output_folder, 'Best')
            if not os.path.exists(best_folder):
                os.makedirs(best_folder)

            ydl_opts = {
                'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'progress_hooks': [self.yt_download_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([yt_url])
                    self.file_label.config(text=f"Download completed! Video saved in: {output_folder}")
                    messagebox.showinfo("Success", f"Download completed successfully! Video saved in: {output_folder}")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred while downloading: {e}")
        else:
            messagebox.showerror("Error", "No YouTube link or folder name provided!")

    def yt_download_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percent = downloaded_bytes / total_bytes * 100
                self.download_progress['value'] = percent
                self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.download_progress['value'] = 100

    def generate_clips_thread(self):
        threading.Thread(target=self.generate_clips).start()

    def generate_clips(self):
        if not self.config:
            messagebox.showerror("Error", "Please run the setup first.")
            return

        folder_name = self.folder_name_entry.get()
        if not folder_name:
            messagebox.showerror("Error", "Please enter a folder name first.")
            return

        output_folder = os.path.join(self.config['downloads_folder'], folder_name)
        video_files = [f for f in os.listdir(output_folder) if f.endswith('.mp4')]

        if len(video_files) == 1:
            video_file = os.path.join(output_folder, video_files[0])
        else:
            messagebox.showerror("Error", "No video file found or multiple video files found.")
            return

        try:
            video = VideoFileClip(video_file)
            video_duration = int(video.duration)

            num_clips = int(self.num_clips_entry.get())
            clip_length = int(self.clip_length_entry.get())
            base_name = self.name_entry.get()

            self.clip_progress["value"] = 0
            self.clip_progress["maximum"] = num_clips

            if self.random_choice.get():
                timecodes = [random.randint(0, max(0, video_duration - clip_length)) for _ in range(num_clips)]
            else:
                timecode_str = self.timecodes_entry.get()
                timecodes = [int(tc.strip()) for tc in timecode_str.split(",") if tc.strip().isdigit()]

            total_clips = len(timecodes)
            self.clip_progress["maximum"] = total_clips

            for i, start_time in enumerate(timecodes):
                start_time = min(start_time, video_duration - clip_length)
                clip = video.subclip(start_time, min(start_time + clip_length, video_duration))
                center_x = clip.w / 2
                vertical_clip = clip.crop(x_center=center_x, width=1080, height=1920).resize(newsize=(1080, 1920))

                output_filename = f"{base_name}_{i + 1}.mp4" if base_name else f"clip_{i + 1}.mp4"
                output_path = os.path.join(output_folder, output_filename)

                vertical_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, threads=4, logger=None)

                self.clip_progress["value"] += 1
                self.root.update_idletasks()
                self.log_output.config(state='normal')
                self.log_output.insert(tk.END, f"Clip {i + 1}/{total_clips} completed: {output_filename}\n")
                self.log_output.see(tk.END)
                self.log_output.config(state='disabled')

            messagebox.showinfo("Success", "All clips generated successfully!")
            self.show_clips_for_evaluation(output_folder)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_clips_for_evaluation(self, clips_folder):
        eval_window = tk.Toplevel(self.root)
        eval_window.title("Evaluate Clips")
        eval_window.geometry("800x600")

        # List all clips
        clip_files = [f for f in os.listdir(clips_folder) if f.endswith('.mp4') and not f.startswith('.')]
        clip_files.sort()

        # Create a listbox to display clips
        clip_listbox = tk.Listbox(eval_window, selectmode=tk.MULTIPLE, width=50)
        clip_listbox.pack(side='left', fill='y', padx=10, pady=10)

        for clip_file in clip_files:
            clip_listbox.insert(tk.END, clip_file)

        # Function to preview clip
        def preview_clip(event):
            selected_indices = clip_listbox.curselection()
            if selected_indices:
                selected_clip = clip_listbox.get(selected_indices[0])
                clip_path = os.path.join(clips_folder, selected_clip)
                # Open the clip with the default media player
                if os.name == 'nt':  # For Windows
                    os.startfile(clip_path)
                elif os.name == 'posix':  # For MacOS and Linux
                    os.system(f'open "{clip_path}"')
                else:
                    messagebox.showerror("Error", "Unsupported OS for previewing clips.")

        clip_listbox.bind('<Double-Button-1>', preview_clip)

        # Function to favorite selected clips
        def favorite_clips():
            selected_indices = clip_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "No clips selected.")
                return
            best_folder = os.path.join(clips_folder, "Best")
            if not os.path.exists(best_folder):
                os.makedirs(best_folder)
            for index in selected_indices:
                clip_file = clip_listbox.get(index)
                src = os.path.join(clips_folder, clip_file)
                dst = os.path.join(best_folder, clip_file)
                os.rename(src, dst)
            messagebox.showinfo("Success", "Selected clips have been moved to the 'Best' folder.")
            eval_window.destroy()

        # Button to move selected clips to 'Best' folder
        favorite_button = tk.Button(eval_window, text="Favorite Selected Clips", command=favorite_clips)
        favorite_button.pack(side='bottom', pady=10)

    def upload_videos_thread(self):
        threading.Thread(target=self.upload_videos).start()

    def upload_videos(self):
        if not self.config:
            messagebox.showerror("Error", "Please run the setup first.")
            return

        folder_name = self.folder_name_entry.get()
        if not folder_name:
            messagebox.showerror("Error", "Please enter a folder name first.")
            return

        best_folder = os.path.join(self.config['downloads_folder'], folder_name, "Best")
        video_files = [f for f in os.listdir(best_folder) if f.endswith('.mp4') and not f.startswith('.')]
        if not video_files:
            messagebox.showerror("Error", "No videos found in the 'Best' folder.")
            return

        # Collect custom titles
        video_titles = {}
        for video_file in video_files:
            default_title = os.path.splitext(video_file)[0]
            title = simpledialog.askstring("Input", f"Enter title for {video_file}", initialvalue=default_title)
            if title is None:
                title = default_title
            video_titles[video_file] = title

        # Collect tags
        tags_str = self.tags_entry.get()
        self.TAGS = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

        youtube = self.authenticate_youtube()
        if not youtube:
            messagebox.showerror("Error", "YouTube authentication failed.")
            return

        total_videos = len(video_files)
        self.upload_progress["value"] = 0
        self.upload_progress["maximum"] = total_videos

        for i, video_file in enumerate(video_files):
            video_title = video_titles[video_file]
            video_path = os.path.join(best_folder, video_file)
            try:
                video_id = self.upload_video(youtube, video_path, video_title, self.TAGS)
                self.upload_progress["value"] += 1
                self.root.update_idletasks()
                self.log_output.config(state='normal')
                self.log_output.insert(tk.END, f"{video_title} uploaded (ID: {video_id})\n")
                self.log_output.see(tk.END)
                self.log_output.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while uploading {video_file}: {e}")
                return

        messagebox.showinfo("Success", "All videos uploaded successfully!")

    def authenticate_youtube(self):
        creds = None
        if not self.config:
            return None

        CLIENT_SECRET_FILE = self.config['client_secret_file']

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        youtube = build('youtube', 'v3', credentials=creds)
        return youtube

    def upload_video(self, youtube, video_path, video_title, tags):
        request_body = {
            'snippet': {
                'title': video_title,
                'description': "Uploaded via YouTube API",
                'tags': tags,
                'categoryId': '22'  # 'People & Blogs' category
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False,  # Or True, depending on content
            }
        }

        media_file = MediaFileUpload(video_path, chunksize=-1, mimetype='video/*', resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media_file
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                # Update upload progress if desired
                # self.upload_progress['value'] = progress
                # self.root.update_idletasks()
        return response.get('id')

    def tutorial_window(self):
        tutorial = tk.Toplevel(self.root)
        tutorial.title("App Tutorial")
        tutorial.geometry("600x400")

        tutorial_text = """
Welcome to the App Tutorial!

1. **Download a video from YouTube**:
   - Enter the YouTube link and a folder name.
   - Click 'Download Video'.

2. **Generate short clips from the downloaded video**:
   - Enter the number of clips and clip length.
   - Choose to use random timecodes or specify them manually.
   - Click 'Generate Clips'.

3. **Evaluate and select favorite clips**:
   - A new window will open to preview and select clips.
   - Double-click a clip to preview.
   - Select clips and click 'Favorite Selected Clips'.

4. **Upload selected clips to YouTube**:
   - Enter tags for the videos.
   - Click 'Upload Videos'.
   - Provide custom titles when prompted.
"""

        label = tk.Label(tutorial, text=tutorial_text, justify="left", font=("Arial", 12))
        label.pack(padx=20, pady=20)

        close_button = tk.Button(tutorial, text="Close", command=tutorial.destroy)
        close_button.pack(pady=10)

if __name__ == "__main__":
    app = YouTubeApp()
