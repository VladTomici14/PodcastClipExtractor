from video import Video
from detector import Detector

from alive_progress import alive_bar
import numpy as np
import time
import cv2

class Extractor:
    def __init__(self):
        self.details = None

        self.target_height = None
        self.target_width = None

        self.output_canvas = None
        self.output_canvas_1 = None
        self.output_canvas_2 = None
        self.output_video_16x9 = None

        self.contor1 = False
        self.contor2 = False

        self.video = Video()
        self.detector = Detector()

    def openVideo(self, video_path):
        """
        Function that opens the video based on its path. It also gets all the details regarding it.

        :param video_path: input video path
        :return: input_video variable ready to be opened frame by frame
        """
        input_video = cv2.VideoCapture(video_path)
        self.details = self.video.getVideoDetails(input_video)
        self.video.printDetailsAboutVideo(self.details, input_video)

        return input_video

    def prepareOutputCanvases(self):
        """
        Function for creating all the output canvases that we will be using for the cropping process.

        :return:
            output_canvas: the blank canvas in the scenario where is only 1 face detected (9x16 ratio)
            output_canvas_1: the first blank canvas in the scenario where are 2 faces detected (9x8 ratio)
            output_canvas_2: the second blank canvas in the scenario where are 2 faces detected (9x8 ratio)
            output_video_16x9 the blank canvas for the final output video (9x16 ratio)
        """
        self.target_height = self.details.VIDEO_HEIGHT
        self.target_width = int((9 * self.target_height) / 16)
        if self.target_width % 2 == True: self.target_width = self.target_width - 1
        self.output_canvas = np.zeros((self.target_height, self.target_width, 3), np.uint8)
        self.output_canvas_1 = np.zeros((self.target_height // 2, self.target_width, 3), np.uint8)
        self.output_canvas_2 = np.zeros((self.target_height // 2, self.target_width, 3), np.uint8)
        output_video_path = f"results/output_no_audio.mp4"
        self.output_video_16x9 = cv2.VideoWriter(
            output_video_path,
            cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
            self.details.VIDEO_FPS,
            (self.target_width, self.target_height)
        )

        return self.output_canvas, self.output_canvas_1, self.output_canvas_2, self.output_video_16x9

    def extractVideoFrames(self, input_video):
        """
        Function for extracting all the frames in the video.

        :param input_video: input video variable based on the input video path that was created in the beginning of the process
        :return:
            frames: array of all the frames in the video
            len_faces: array of all the number of faces detected per frame
            faces_arr: array of all the detected faces per frame
        """
        frames = []
        len_faces = []
        faces_arr = []

        k = 0
        # ------------ collecting and processing all the video ------------
        with alive_bar(self.details.VIDEO_NOFRAMES) as bar:
            while input_video.isOpened():
                ret, frame = input_video.read()

                if ret is True:
                    if k % 3 == False:
                        faces = self.detector.detectFaces(frame)
                        no_faces = len(faces)

                    if no_faces > 2:
                        len_faces.append(2)
                    else:
                        len_faces.append(no_faces)

                    faces_arr.append(faces)
                    frames.append(frame)

                    k = k + 1
                    bar()

                else:
                    break

        input_video.release()

        return frames, len_faces, faces_arr

    def cropFrames(self, frames, fin_len_faces, faces_arr, output_video_16x9):
        """
        Function for doing the actual cropping based on the detections that were done when reading the frames.

        :param frames: array of the video frames
        :param fin_len_faces: array of the sorted number of detected faces per frame
        :param faces_arr: array of all the detected faces per frame
        :param output_video_16x9: output canvas for writing all the frames in the end
        """
        for i in range(len(frames)):
            current_frame = frames[i]
            faces = faces_arr[i]

            if not faces:
                if fin_len_faces == len(faces_arr[i - 1]):
                    faces_arr[i] = faces_arr[i - 1]
                    faces = faces_arr[i]
                elif fin_len_faces == len(faces_arr[i + 1]) and len(faces_arr[i - 1]) != len(faces_arr[i + 1]):
                    faces_arr[i] = faces_arr[i + 1]
                    faces = faces_arr[i]

            if len(faces) == 0:
                lim_left = self.details.VIDEO_WIDTH // 2 - self.target_width // 2
                lim_right = self.details.VIDEO_WIDTH // 2 + self.target_width // 2

                self.output_canvas = current_frame[0:self.target_height, lim_left:lim_right]

            if fin_len_faces[i] == 1 and len(faces) != 0:
                if len(faces) == 0:
                    lim_left = self.details.VIDEO_WIDTH // 2 - self.target_width // 2
                    lim_right = self.details.VIDEO_WIDTH // 2 + self.target_width // 2
                else:
                    face = faces[0]
                    x, y, w, h = face["box"]

                    center_face_x, center_face_y = x + w // 2, y + h // 2

                    if self.contor1 == False:
                        lim_left = center_face_x - self.target_width // 2
                        lim_right = center_face_x + self.target_width // 2

                        self.contor1 = True

                    # ------------ condition of changing the camera if the face is waaaaaay too moved ------------
                    if not (lim_left + 100 < center_face_x < lim_right - 100):
                        lim_left = center_face_x - self.target_width // 2
                        lim_right = center_face_x + self.target_width // 2

                    if lim_left < 0:
                        lim_left = 0
                        lim_right = self.target_width

                    if lim_right > self.details.VIDEO_WIDTH:
                        lim_right = self.details.VIDEO_WIDTH
                        lim_left = self.details.VIDEO_WIDTH - self.target_width

                    print(f"frame {i} -- lim_left: {lim_left} -- lim_right: {lim_right}")
                    print(f"target_height {i}: {self.target_height}")

                self.output_canvas = current_frame[0:self.target_height, lim_left:lim_right]

            elif fin_len_faces[i] == 2:
                if len(faces) == 1:
                    face1 = faces[0]
                    x1, y1, w1, h1 = face1["box"]
                else:
                    face1 = faces[0]
                    x1, y1, w1, h1 = face1["box"]
                    face2 = faces[1]
                    x2, y2, w2, h2 = face2["box"]

                center_face_x1, center_face_y1 = x1 + w1 // 2, y1 + h1 // 2
                center_face_x2, center_face_y2 = x2 + w2 // 2, y2 + h2 // 2

                if self.contor2 == False:
                    lim_left1 = center_face_x1 - self.target_width // 2
                    lim_right1 = center_face_x1 + self.target_width // 2
                    lim_up1 = center_face_y1 - (self.target_height // 2) // 2
                    lim_down1 = center_face_y1 + (self.target_height // 2) // 2
                    if lim_up1 < 0:
                        lim_up1 = 0
                        lim_down1 = self.target_height // 2
                    if lim_down1 > self.details.VIDEO_HEIGHT:
                        lim_down1 = self.details.VIDEO_HEIGHT
                        lim_up1 = self.target_height // 2
                    if lim_left1 < 0:
                        lim_left1 = 0
                        lim_right1 = self.target_width
                    if lim_right1 > self.details.VIDEO_WIDTH:
                        lim_right1 = self.details.VIDEO_WIDTH
                        lim_left1 = self.details.VIDEO_WIDTH - self.target_width

                    lim_left2 = center_face_x2 - self.target_width // 2
                    lim_right2 = center_face_x2 + self.target_width // 2
                    lim_up2 = center_face_y2 - (self.target_height // 2) // 2
                    lim_down2 = center_face_y2 + (self.target_height // 2) // 2
                    if lim_up2 < 0:
                        lim_up2 = 0
                        lim_down2 = self.target_height // 2
                    if lim_down2 > self.details.VIDEO_HEIGHT:
                        lim_down2 = self.details.VIDEO_HEIGHT
                        lim_up2 = self.target_height // 2
                    if lim_left2 < 0:
                        lim_left2 = 0
                        lim_right2 = self.target_width
                    if lim_right2 > self.details.VIDEO_WIDTH:
                        lim_right2 = self.details.VIDEO_WIDTH
                        lim_left2 = self.details.VIDEO_WIDTH - self.target_width

                    self.contor2 = True

                # ------------ taking the ROI from the video ------------
                if current_frame[lim_up1:lim_down1, lim_left1:lim_right1].shape == self.output_canvas_1.shape:
                    self.output_canvas_1 = current_frame[lim_up1:lim_down1, lim_left1:lim_right1]
                if current_frame[lim_up2:lim_down2, lim_left2:lim_right2].shape == self.output_canvas_2.shape:
                    self.output_canvas_2 = current_frame[lim_up2:lim_down2, lim_left2:lim_right2]

                center_video_x = min(center_face_x1, center_face_x2) + abs(center_face_x1 - center_face_x2) // 2

                # ------------ ordering the speakers ------------
                if lim_right1 < center_video_x:
                    self.output_canvas_1 = current_frame[lim_up1:lim_down1, lim_left1:lim_right1]
                    self.output_canvas_2 = current_frame[lim_up2:lim_down2, lim_left2:lim_right2]
                elif lim_left1 > center_video_x:
                    self.output_canvas_1 = current_frame[lim_up2:lim_down2, lim_left2:lim_right2]
                    self.output_canvas_2 = current_frame[lim_up1:lim_down1, lim_left1:lim_right1]

                latest_config = 2

                # ------------ adding the ROIs into the 8:9 ratio ------------
                self.output_canvas[0:self.target_height // 2, 0:self.target_width] = self.output_canvas_1
                self.output_canvas[self.target_height // 2: self.target_height, 0:self.target_width] = self.output_canvas_2

            output_video_16x9.write(self.output_canvas)

        output_video_16x9.release()

    def extractOutputVideo(self, video_path):
        """
        Basically the main function of the detection that contains all the steps for the whole process of detecting.

        :param video_path: the path of the input video
        """

        # ------------ opening the video & getting details from it ------------
        input_video = self.openVideo(video_path)

        # ------------ preparing the output canvas ------------
        self.output_canvas, self.output_canvas_1, self.output_canvas_2, output_video_16x9 = self.prepareOutputCanvases()

        # ------------ collecting and processing all the video ------------
        frames, len_faces, faces_arr = self.extractVideoFrames(input_video)

        # ------------ sorting the data ------------
        print(len_faces)
        fin_len_faces, faces_arr = self.detector.sortArr(len_faces, faces_arr)
        fin_len_faces = self.detector.secondSorter(fin_len_faces)

        # ------------ cropping the video ------------
        self.cropFrames(frames, fin_len_faces, faces_arr, output_video_16x9)

        # ------------ releasing the video usage ------------
        input_video.release()
        cv2.destroyAllWindows()

        # ------------ waiting some time for the file to fully write on the computer ------------
        time.sleep(5)
