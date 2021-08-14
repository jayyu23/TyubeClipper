from pytube import YouTube
import ssl

ssl._create_default_https_context = ssl._create_stdlib_context
chunk_size = 1024


def convert_youtube(yt_link, on_progress, mode):
    yt = YouTube(yt_link)
    yt_vid = yt.streams.filter(progressive=True, file_extension='mp4',
                               only_audio=(mode == "audio"), only_video=(mode == "video"))\
                        .order_by('resolution').first()
    yt.register_on_progress_callback(on_progress)
    return yt_vid


def download_youtube(yt_vid, out_file):
    yt_vid.download(output_path=out_file)
