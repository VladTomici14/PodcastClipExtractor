from extractor import Extractor
import argparse
import time
import moviepy.editor as mpe

# ------------ argparsing the video path ------------
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True)
args = vars(ap.parse_args())

# ------------ declaring the class for the process ------------
extractor = Extractor()

# ------------ creating the output video ------------
extractor.extractOutputVideo(args["input"])

# ------------ adding audio to clip ------------
def addAudioToClip(video_path, input_audio_path):
    """
    Function for adding audio on the video.

    :param video_path: the output video on which we want to add the audio
    :param input_audio_path: the original video file that contains the audio
    """
    clip = mpe.VideoFileClip(video_path)
    input_audio_clip = mpe.VideoFileClip(input_audio_path)
    final_clip = clip.set_audio(input_audio_clip.audio)
    final_clip.write_videofile("results/output.mp4")


addAudioToClip(str("results/output_no_audio.mp4"), str(args["input"]))
