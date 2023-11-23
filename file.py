import tkinter as tk
from tkinter import filedialog, messagebox
import pytube
import os
from pytube.exceptions import PytubeError
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk
from tqdm import tqdm

class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader by mahmoud omar")

        self.url_label = tk.Label(master, text="Enter video or playlist URL:")
        self.url_label.pack()

        self.url_entry = tk.Entry(master, width=120)
        self.url_entry.pack()

        self.output_label = tk.Label(master, text="Choose output path:")
        self.output_label.pack()

        self.output_button = tk.Button(master, text="Select Folder", command=self.choose_output_path)
        self.output_button.pack()

        self.download_type_var = tk.StringVar()
        self.download_type_var.set("video")

        self.download_type_label = tk.Label(master, text="Select download type:")
        self.download_type_label.pack()

        self.video_radio = tk.Radiobutton(master, text="Video", variable=self.download_type_var, value="video")
        self.video_radio.pack()

        self.playlist_radio = tk.Radiobutton(master, text="Playlist", variable=self.download_type_var, value="playlist")
        self.playlist_radio.pack()

        self.quality_label = tk.Label(master, text="Choose video quality:")
        self.quality_label.pack()

        self.quality_var = tk.StringVar()
        self.quality_var.set("highest")

                # استخدمت set() للتأكد من عدم وجود تكرار في القيم
        self.quality_options = list(set(["highest", "lowest"]))

        self.quality_menu = ttk.Combobox(master, textvariable=self.quality_var, values=self.quality_options)
        self.quality_menu.pack()

        self.audio_only_var = tk.BooleanVar()
        self.audio_only_var.set(False)

        self.audio_only_checkbox = tk.Checkbutton(master, text="Download audio only", variable=self.audio_only_var)
        self.audio_only_checkbox.pack()

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(master, variable=self.progress_var, mode='determinate')
        self.progress_bar.pack()

        self.download_button = tk.Button(master, text="Download", command=self.download)
        self.download_button.pack()

    def choose_output_path(self):
        output_path = filedialog.askdirectory()
        if output_path:
            self.output_path = output_path

    def on_quality_change(self, event):
        if self.quality_var.get().endswith("p"):
            custom_quality = int(self.quality_var.get().split("p")[0])
            self.custom_quality = custom_quality

    def download_video(self, video_url):
        download_audio = self.audio_only_var.get()

        try:
            video = pytube.YouTube(video_url)
            if download_audio:
                stream = video.streams.filter(only_audio=True).first()
            else:
                selected_option = self.quality_var.get()
                if selected_option == "highest":
                    stream = video.streams.get_highest_resolution()
                elif selected_option == "lowest":
                    stream = video.streams.get_lowest_resolution()
                else:
                    stream = self.get_selected_stream(video, selected_option)

            valid_folder_name = "".join(c for c in video.title if c.isalnum() or c in [' ', '_', '-'])
            download_path = os.path.join(self.output_path, valid_folder_name)
            os.makedirs(download_path, exist_ok=True)

            # Download the video without using on_progress
            with tqdm(total=stream.filesize, unit='B', unit_scale=True, desc=f"Downloading {video.title}") as bar:
                stream.download(download_path)
            bar.close()

            if download_audio:
                base_filename = os.path.splitext(stream.title)[0]
                output_audio_path = os.path.join(download_path, f"{base_filename}.mp3")
                os.rename(os.path.join(download_path, stream.title), output_audio_path)

            messagebox.showinfo("Download Complete", f"Download of {video.title} successful!")
        except PytubeError as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def get_selected_stream(self, video, selected_option):
        streams = video.streams.filter(type="video", progressive=True)
        for stream in streams:
            if selected_option in str(stream):
                return stream

    def download(self):
        url = self.url_entry.get()
        download_audio = self.audio_only_var.get()

        # Validate URL
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        # Validate output path
        if not hasattr(self, 'output_path'):
            messagebox.showerror("Error", "Please choose an output folder.")
            return

        try:
            if "playlist" in url.lower():
                self.download_playlist(url)
            else:
                self.download_video(url)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def update_progress(self, bytes_remaining):
        total_bytes = self.progress_var.get()
        remaining_bytes = bytes_remaining
        progress_percentage = ((total_bytes - remaining_bytes) / total_bytes) * 100
        self.progress_var.set(progress_percentage)

    def download_playlist(self, playlist_url):
        # تحميل جميع الفيديوهات في البلاي ليست
        playlist = pytube.Playlist(playlist_url)
        for video_url in playlist.video_urls:
            self.download_video(video_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
