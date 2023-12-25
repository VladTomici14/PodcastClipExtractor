import moviepy.editor as mpe
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True)
ap.add_argument("-a", "--audio", required=True)
args = vars(ap.parse_args())

clip = mpe.VideoFileClip(args["input"])
input_audio_clip = mpe.VideoFileClip(args["audio"])
final_clip = clip.set_audio(input_audio_clip.audio)
final_clip.write_videofile("output.mp4")
