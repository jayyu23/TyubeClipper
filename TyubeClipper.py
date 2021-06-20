import functools
import tkinter as tk
from concurrent import futures
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import Progressbar

import converter as cv

VERSION = 0.2

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)


def tk_after(target):
    @functools.wraps(target)
    def wrapper(self, *args, **kwargs):
        args = (self,) + args
        self.after(0, target, *args, **kwargs)

    return wrapper


def submit_to_pool_executor(executor):
    def decorator(target):
        @functools.wraps(target)
        def wrapper(*args, **kwargs):
            return executor.submit(target, *args, **kwargs)

        return wrapper

    return decorator


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    complete_pct = round((bytes_downloaded / total_size) * 100, 2)
    comp_txt = f"Download Progress: {complete_pct}%"
    main_frame.set_result_label(comp_txt)
    main_frame.update_determinate_pbar(complete_pct)
    print(comp_txt)

class MainFrame(tk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.master.geometry('600x250')
        self.master.title(f'Tyube Clipper v{VERSION}')
        self.options = {'padx': 5, 'pady': 5}
        self.yt_vid = None

        # Row 0, Row 1 - Title Subtitle
        title_label = tk.Label(self.master, text="Tyube Clipper", font=("Helvetica", 25))
        subtitle_label = tk.Label(self.master, text="Lightweight YouTube to MP4 Converter, brought to you by J.Yu")
        title_label.grid(columnspan=5, row=0, sticky='W', **self.options)
        subtitle_label.grid(columnspan=5, row=1, sticky="W", **self.options)

        # Row 2 - Link Entry + Convert Download Buttons
        link_label = tk.Label(self.master, text='Youtube Link')
        self.link = tk.StringVar()
        self.link_entry = tk.Entry(self.master, textvariable=self.link)
        self.link_entry.focus()
        convert_button = tk.Button(self.master, text='Convert')
        convert_button.configure(command=self.convert_button_clicked)
        download_button = tk.Button(self.master, text='Download')
        download_button.configure(command=self.download_button_clicked)
        # Make into grid
        link_label.grid(column=0, row=2, sticky='W', **self.options)
        self.link_entry.grid(column=1, columnspan=2, row=2, **self.options)
        convert_button.grid(column=3, row=2, sticky='W', **self.options)
        download_button.grid(column=4, row=2, sticky='W', **self.options)

        # Row 3 - Radio buttons
        self.mode_opt = tk.StringVar()
        r1 = tk.Radiobutton(self.master, text="Audio & Video", variable=self.mode_opt, value="both")
        r2 = tk.Radiobutton(self.master, text="Audio Only", variable=self.mode_opt, value="audio")
        r3 = tk.Radiobutton(self.master, text="Video Only", variable=self.mode_opt, value="video")
        r1.select()
        r1.grid(column=0, row=3, **self.options)
        r2.grid(column=1, row=3, **self.options)
        r3.grid(column=2, row=3, **self.options)

        # Row 4 - Result label
        self.result_label = tk.Label(self.master)
        self.result_label.grid(row=4, columnspan=3, **self.options)

        # Row 5 - Progress Bar
        self.progress_bar = None

    @tk_after
    def set_result_label(self, text):
        self.result_label.config(text=text)

    @tk_after
    def set_indeterminate_pbar(self):
        self.progress_bar = Progressbar(self.master, length=150, mode="indeterminate")
        self.progress_bar.grid(row=5, column=1)
        self.progress_bar.start()

    @tk_after
    def setup_determinate_pbar(self):
        self.progress_bar = Progressbar(self.master, length=150, mode="determinate")
        self.progress_bar['value'] = 0
        self.progress_bar.grid(row=5, column=1)

    @tk_after
    def update_determinate_pbar(self, value):
        self.progress_bar['value'] = value

    @submit_to_pool_executor(thread_pool_executor)
    def convert_button_clicked(self):
        l = self.link.get()
        mode = self.mode_opt.get()
        self.set_result_label("Fetching from source... Please wait")
        self.set_indeterminate_pbar()
        self.yt_vid = cv.convert_youtube(l, on_progress, mode)
        result = f'{self.yt_vid.title}\nFile size: {self.yt_vid.filesize * 10 ** -6:.3f} MB'
        self.set_result_label(result)
        self.setup_determinate_pbar()

    @submit_to_pool_executor(thread_pool_executor)
    def download_button_clicked(self):
        if self.yt_vid:
            self.set_result_label("Downloading... Please wait")
            f = asksaveasfilename(initialfile=f"{self.yt_vid.title}.mp4",
                                  defaultextension=".mp4",
                                  filetypes=[("MPEG-4 File", "*.mp4")])
            if not f:
                return
            cv.download_youtube(self.yt_vid, f)
            self.set_result_label("Download Complete!")


if __name__ == '__main__':
    app = tk.Tk()
    app.title(f'Tyube Clipper v{VERSION}')
    main_frame = MainFrame()
    app.mainloop()
