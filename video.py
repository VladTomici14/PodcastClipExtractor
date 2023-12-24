import numpy as np
import cv2


class Video:
    def __init__(self):
        pass

    def getVideoDetails(self, video):
        """
        Getting all the details from a video.
            :param video: input video

        :return: all the details of the video in a VideoDetails variable
        """
        details = VideoDetails()
        details.VIDEO_FPS = video.get(cv2.CAP_PROP_FPS)
        (details.VIDEO_HEIGHT, details.VIDEO_WIDTH) = video.read()[1].shape[:2]
        details.VIDEO_NOFRAMES = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        details.VIDEO_DURATION = details.VIDEO_NOFRAMES / details.VIDEO_FPS

        return details

    def printDetailsAboutVideo(self, details, filename):
        print(f"video_path: {filename}")
        print(f"video_fps: {details.VIDEO_FPS}")
        print(f"video_width: {details.VIDEO_WIDTH}")
        print(f"video_height: {details.VIDEO_HEIGHT}")
        print(f"video_duration: {details.VIDEO_DURATION} seconds")

    def calculateTargetShapes(self, image, width_ratio, height_ratio):
        (current_height, current_width) = image.shape[:2]

        target_width = int((width_ratio * current_height) / height_ratio)
        target_height = current_height

        if target_width % 2 == False:
            target_width -= 1

        return target_width, target_height


class VideoDetails:
    VIDEO_FPS: int
    VIDEO_WIDTH: int
    VIDEO_HEIGHT: int
    VIDEO_NOFRAMES: int
    VIDEO_DURATION: float


class FRAMES:
    FRAME: np.array
    NO_PEOPLE: int
