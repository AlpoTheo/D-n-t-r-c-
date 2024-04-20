import tkinter as tk
from tkinter import filedialog, messagebox
from pytube import YouTube
from moviepy.editor import AudioFileClip
import threading
import os

class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        self.master.title("YouTube MP3 Downloader")

        tk.Label(master, text="YouTube Video URL:").pack()
        
        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack()

        self.download_button = tk.Button(master, text="Download", command=self.start_download_thread)
        self.download_button.pack()

        self.is_downloading = False  # Track whether a download is in progress

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "URL cannot be empty!")
            return
        
        if not self.validate_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL!")
            return

        output_path = filedialog.askdirectory()
        if not output_path:  # Check if the user canceled the folder selection
            return

        if self.is_downloading:
            return  # Prevent multiple downloads if user rapidly clicks

        self.is_downloading = True
        self.download_button.config(state=tk.DISABLED)  # Disable the download button
        
        try:
            video = YouTube(url)
            stream = video.streams.filter(only_audio=True).first()
            if stream is None:
                messagebox.showerror("Error", "No audio stream found!")
                return
            downloaded_file = stream.download(output_path)
            
            if not os.path.exists(downloaded_file):
                messagebox.showerror("Error", "Downloaded file does not exist!")
                return

            try:
                video_clip = AudioFileClip(downloaded_file)
            except Exception as e:
                messagebox.showerror("Error", "Failed to load video file: " + str(e))
                os.remove(downloaded_file)  # Remove the downloaded MP4 file if conversion fails
                return
            
            mp3_file = downloaded_file.replace('.mp4', '.mp3')
            video_clip.write_audiofile(mp3_file)
            video_clip.close()
            os.remove(downloaded_file)  # Delete the MP4 file
            messagebox.showinfo("Success", "MP3 downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.is_downloading = False
            self.download_button.config(state=tk.NORMAL)  # Re-enable the download button

    def validate_url(self, url):
        # Validate the YouTube URL using regex
        import re
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        youtube_regex_match = re.match(youtube_regex, url)
        return youtube_regex_match is not None

    def start_download_thread(self):
        if not self.is_downloading:
            threading.Thread(target=self.download_video, daemon=True).start()

# GUI Setup
root = tk.Tk()
app = YouTubeDownloader(root)
root.mainloop()
