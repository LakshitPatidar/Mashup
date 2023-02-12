from django.core.mail import send_mail,EmailMessage
from django.shortcuts import render
import os
import moviepy.editor as mp
import sys
from pytube import YouTube, Search
from .forms import MashupForm
import shutil

def send_email(to_email, file_path):
    subject = 'Mashup Result'
    message = 'Please find the attached Mashup Audio'
    email = EmailMessage(
        subject, message, to=[to_email]
    )
    email.attach_file(file_path)
    email.send()

def download_videos(singer, num_videos):
    videos = []
    search_query = singer
    search_result = Search(search_query)
    for video in search_result.results:
        video_url = f"{video.watch_url}"
        yt = YouTube(video_url)
        if yt.length <= 600 and yt.streams.filter(res="144p").first() is not None:
            videos.append(yt)
        if len(videos) == num_videos:
            break
    if len(videos) < num_videos:
        print("def")
        raise Exception("Unable to find {} videos of {} with resolution 144p and duration less than 5 minutes.".format(num_videos, singer))
    return videos

def convert_to_audio(video, singer):
    audio = video.streams.filter(only_audio=True).first()
    audio_file = os.path.join(singer, f"{video.title}.mp3")
    audio.download(filename=audio_file)
    return audio_file

def cut_audio(audio_file, duration):
    clip = mp.AudioFileClip(audio_file).subclip(0, duration)
    return clip

def merge_audios(audios, output_file):
    final_audio = mp.concatenate_audioclips(audios)
    final_audio.write_audiofile(output_file)

def main(request):
    if request.method == 'POST':
        form = MashupForm(request.POST)
        print("abc")
        if form.is_valid():
            singer = form.cleaned_data['singer_name']
            num_videos = form.cleaned_data['number_of_videos']
            duration = form.cleaned_data['duration']
            email = form.cleaned_data['email']
            try:
                if num_videos <= 10 or duration <= 20:
                    raise Exception("num of videos should be greater than 10 and duration should be greater than 20")
                singer_folder = os.path.join(os.getcwd(), singer)
                if not os.path.exists(singer_folder):
                    os.makedirs(singer_folder)
                videos = download_videos(singer, num_videos)
                for video in videos:
                    video.streams.filter(res="144p").first().download(filename=os.path.join(singer_folder, f"{video.title}.mp4"))
                audios = []
                for video in videos:
                    audio_file = convert_to_audio(video, singer)
                    clip = cut_audio(audio_file, duration)
                    audios.append(clip)
                output_file = os.path.join(singer_folder, "mashup.mp3")
                merge_audios(audios, output_file)
                send_email(email, output_file)
                shutil.rmtree(singer_folder)
                return render(request, 'success.html')
            except Exception as e:
                print(str(e))
                return render(request, 'error.html', {'message': str(e)})
    else:
        form = MashupForm()
        return render(request, 'main.html', {'form': form})
