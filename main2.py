"""
TODO list:
- write documentation for the project
    - like how long did it take for the program to load for 4k footage, things like that.
    - make some plots with the results for showing to the project
- implement audio switch
- write install guide
- remove false-positives (https://github.com/davidsandberg/facenet/issues/456)
"""

from timeit import default_timer as timer
from datetime import datetime
import numpy as np
import argparse
import cv2

from video import Video
from detector import Detector, Draw

# ------------ starting the timer ------------
start_timer = timer()

# ------------ argparsing the input video path ------------
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="input path of the video")
args = vars(ap.parse_args())

# ------------ declaring all the classes that we'll use ------------
video, detector, draw = Video(), Detector(), Draw()

# ------------ opening the video & getting details from it ------------
input_video = cv2.VideoCapture(args["input"])
details = video.getVideoDetails(input_video)
print(f"video_path: {args['input']}")
print(f"video_fps: {details.VIDEO_FPS}")
print(f"video_width: {details.VIDEO_WIDTH}")
print(f"video_height: {details.VIDEO_HEIGHT}")
print(f"video_duration: {details.VIDEO_DURATION} seconds")

# ------------ handling the video audio ------------
"""
Maybe try to take the audio from the input video and just to stick it in the end to the output video. 
"""

# ------------ preparing output canvas ------------
target_height = details.VIDEO_HEIGHT
target_width = int((9 * target_height) / 16)
if target_width % 2 == True: target_width = target_width - 1
output_canvas = np.zeros((target_height, target_width, 3), np.uint8)

output_canvas_1 = np.zeros((target_height // 2, target_width, 3), np.uint8)
output_canvas_2 = np.zeros((target_height // 2, target_width, 3), np.uint8)

output_video_16x9 = cv2.VideoWriter(
    f"results/result-{datetime.now()}.mp4",
    cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
    details.VIDEO_FPS,
    (target_width, target_height)
)

frames = []
len_faces = []
faces_arr = []

no_frames1, no_frames2 = 1, 1
median_face_area = 0
while input_video.isOpened():
    ret, frame = input_video.read()

    if ret is True:
        faces = detector.detectFaces(frame)

        frames.append(frame)
        len_faces.append(len(faces))
        faces_arr.append(faces)

        if len(faces) == 1:
            face = faces[0]
            x, y, w, h = face["box"]
            face_area = w * h

            center_face_x, center_face_y = x + w // 2, y + h // 2

            if no_frames1 == 1:
                lim_left = center_face_x - target_width // 2
                lim_right = center_face_x + target_width // 2

            # ------------ condition of changing the camera if the face is waaaaaay too moved ------------
            """
            Basically in the 1-face scenario, we save the first ROI based on the first face that it was detected.

            Based on that ROI, we will keep it until the center_face_x moves waaaaay too much.

            Maybe add a fault counter for entering that zone
            """
            if not (lim_left + 100 < center_face_x < lim_right - 100):
                lim_left = center_face_x - target_width // 2
                lim_right = center_face_x + target_width // 2

            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
            # cv2.circle(frame, (center_face_x, center_face_y), 4, (0, 255, 0), -1)

            latest_config = 1

            no_frames1 += 1
            output_canvas = frame[0:target_height, lim_left:lim_right]

        elif len(faces) == 2:
            face1 = faces[0]
            x1, y1, w1, h1 = face1["box"]
            face_area1 = w1 * h1

            face2 = faces[1]
            x2, y2, w2, h2 = face2["box"]
            face_area2 = w2 * h2

            center_face_x1, center_face_y1 = x1 + w1 // 2, y1 + h1 // 2
            center_face_x2, center_face_y2 = x2 + w2 // 2, y2 + h2 // 2

            if no_frames2 == 1:
                lim_left1 = center_face_x1 - target_width // 2
                lim_right1 = center_face_x1 + target_width // 2
                lim_up1 = center_face_y1 - (target_height // 2) // 2
                lim_down1 = center_face_y1 + (target_height // 2) // 2

                lim_left2 = center_face_x2 - target_width // 2
                lim_right2 = center_face_x2 + target_width // 2
                lim_up2 = center_face_y2 - (target_height // 2) // 2
                lim_down2 = center_face_y2 + (target_height // 2) // 2

            # ------------ condition of changing the camera if the face is waaaaaay too moved ------------
            """
            Basically in the 1-face scenario, we save the first ROI based on the first face that it was detected.

            Based on that ROI, we will keep it until the center_face_x moves waaaaay too much.

            Maybe add a fault counter for entering that zone
            """
            # if not (lim_left1 + 25 < center_face_x1 < lim_right1 - 25):
            #     lim_left1 = center_face_x1 - target_width // 2
            #     lim_right1 = center_face_x1 + target_width // 2
            # if not (lim_up1 + 25 < center_face_y1 < lim_down1 - 25):
            #     lim_up1 = center_face_y1 - (target_height // 2) // 2
            #     lim_down1 = center_face_y1 + (target_height // 2) // 2
            #
            # if not (lim_left2 + 25 < center_face_x2 < lim_right2 - 25):
            #     lim_left2 = center_face_x2 - target_width // 2
            #     lim_right2 = center_face_x2 + target_width // 2
            # if not (lim_up2 + 24 < center_face_y2 < lim_right2 - 25):
            #     lim_up2 = center_face_y2 - (target_height // 2) // 2
            #     lim_down2 = center_face_y2 + (target_height // 2) // 2

            no_frames2 += 1

            # ------------ taking the ROI from the video ------------
            output_canvas_1 = frame[lim_up1:lim_down1, lim_left1:lim_right1]
            output_canvas_2 = frame[lim_up2:lim_down2, lim_left2:lim_right2]

            center_video_x = min(center_face_x1, center_face_x2) + abs(center_face_x1 - center_face_x2) // 2

            # ------------ drawing bounding rectangle around the detected faces ------------
            # cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 5)
            # cv2.circle(frame, (center_face_x1, center_face_y1), 4, (0, 255, 0), -1)
            #
            # cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 5)
            # cv2.circle(frame, (center_face_x2, center_face_y2), 4, (0, 255, 0), -1)
            #
            # cv2.circle(frame, (center_video_x, details.VIDEO_HEIGHT // 2), 10, (255, 0, 0), -1)

            # cv2.putText(frame, str(face1["confidence"]), (center_face_x1, center_face_y1), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3, cv2.LINE_AA)
            # cv2.putText(frame, str(face2["confidence"]), (center_face_x2, center_face_y2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3, cv2.LINE_AA)

            if lim_right1 < center_video_x:
                output_canvas_1 = frame[lim_up1:lim_down1, lim_left1:lim_right1]
                output_canvas_2 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
            elif lim_left1 > center_video_x:
                output_canvas_1 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
                output_canvas_2 = frame[lim_up1:lim_down1, lim_left1:lim_right1]

            latest_config = 2


            # ------------ adding the ROIs into the 8:9 ratio ------------
            output_canvas[0:target_height // 2, 0:target_width] = output_canvas_1
            output_canvas[target_height // 2: target_height, 0:target_width] = output_canvas_2

        else:
            if latest_config == 1:
                if not (lim_left + 100 < center_face_x < lim_right - 100):
                    lim_left = center_face_x - target_width // 2
                    lim_right = center_face_x + target_width // 2

                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                # cv2.circle(frame, (center_face_x, center_face_y), 4, (0, 255, 0), -1)

                latest_config = 1

                no_frames1 += 1
                output_canvas = frame[0:target_height, lim_left:lim_right]

            elif latest_config == 2:
                if lim_right1 < center_video_x:
                    output_canvas_1 = frame[lim_up1:lim_down1, lim_left1:lim_right1]
                    output_canvas_2 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
                elif lim_left1 > center_video_x:
                    output_canvas_1 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
                    output_canvas_2 = frame[lim_up1:lim_down1, lim_left1:lim_right1]

                latest_config = 2

                # ------------ adding the ROIs into the 8:9 ratio ------------
                output_canvas[0:target_height // 2, 0:target_width] = output_canvas_1
                output_canvas[target_height // 2: target_height, 0:target_width] = output_canvas_2



        # cv2.putText(output_canvas, f"no faces: {str(len(faces))}", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0),
        #             3, cv2.LINE_AA)

        # ------------ saving the frames into the output video ------------
        output_video_16x9.write(output_canvas)

        # ------------ showing the image ------------
        cv2.imshow("frame", output_canvas)
        cv2.imshow("output_canvas_1", output_canvas_1)
        cv2.imshow("output_canvas_2", output_canvas_2)
        if cv2.waitKey(1) == ord("q"):
            break

    else:
        break

# len_faces = detector.sortArr(len_faces)
#
# for i in range(len(frames)):
#     current_frame = frames[i]
#     current_len_faces = len_faces[i]
#     faces = faces_arr[i]
#
#     if current_len_faces == 1:
#         face = faces[0]
#         x, y, w, h = face["box"]
#         face_area = w * h
#
#         center_face_x, center_face_y = x + w // 2, y + h // 2
#
#         if no_frames1 == 1:
#             lim_left = center_face_x - target_width // 2
#             lim_right = center_face_x + target_width // 2
#
#         # ------------ condition of changing the camera if the face is waaaaaay too moved ------------
#         """
#         Basically in the 1-face scenario, we save the first ROI based on the first face that it was detected.
#
#         Based on that ROI, we will keep it until the center_face_x moves waaaaay too much.
#
#         Maybe add a fault counter for entering that zone
#         """
#         if not (lim_left + 100 < center_face_x < lim_right - 100):
#             lim_left = center_face_x - target_width // 2
#             lim_right = center_face_x + target_width // 2
#
#         # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
#         # cv2.circle(frame, (center_face_x, center_face_y), 4, (0, 255, 0), -1)
#
#         no_frames1 += 1
#         output_canvas = frame[0:target_height, lim_left:lim_right]
#
#     elif current_len_faces == 2:
#         face1 = faces[0]
#         x1, y1, w1, h1 = face1["box"]
#         face_area1 = w1 * h1
#
#         face2 = faces[1]
#         x2, y2, w2, h2 = face2["box"]
#         face_area2 = w2 * h2
#
#         center_face_x1, center_face_y1 = x1 + w1 // 2, y1 + h1 // 2
#         center_face_x2, center_face_y2 = x2 + w2 // 2, y2 + h2 // 2
#
#         if no_frames2 == 1:
#             lim_left1 = center_face_x1 - target_width // 2
#             lim_right1 = center_face_x1 + target_width // 2
#             lim_up1 = center_face_y1 - (target_height // 2) // 2
#             lim_down1 = center_face_y1 + (target_height // 2) // 2
#
#             lim_left2 = center_face_x2 - target_width // 2
#             lim_right2 = center_face_x2 + target_width // 2
#             lim_up2 = center_face_y2 - (target_height // 2) // 2
#             lim_down2 = center_face_y2 + (target_height // 2) // 2
#
#         # ------------ condition of changing the camera if the face is waaaaaay too moved ------------
#         """
#         Basically in the 1-face scenario, we save the first ROI based on the first face that it was detected.
#
#         Based on that ROI, we will keep it until the center_face_x moves waaaaay too much.
#
#         Maybe add a fault counter for entering that zone
#         """
#         if not (lim_left1 + 50 < center_face_x1 < lim_right1 - 50):
#             lim_left1 = center_face_x1 - target_width // 2
#             lim_right1 = center_face_x1 + target_width // 2
#         if not (lim_up1 + 25 < center_face_y1 < lim_down1 - 25):
#             lim_up1 = center_face_y1 - (target_height // 2) // 2
#             lim_down1 = center_face_y1 + (target_height // 2) // 2
#
#         if not (lim_left2 + 50 < center_face_x2 < lim_right2 - 50):
#             lim_left2 = center_face_x2 - target_width // 2
#             lim_right2 = center_face_x2 + target_width // 2
#         if not (lim_up2 + 24 < center_face_y2 < lim_right2 - 25):
#             lim_up2 = center_face_y2 - (target_height // 2) // 2
#             lim_down2 = center_face_y2 + (target_height // 2) // 2
#
#         no_frames2 += 1
#
#         # ------------ taking the ROI from the video ------------
#         output_canvas_1 = frame[lim_up1:lim_down1, lim_left1:lim_right1]
#         output_canvas_2 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
#
#         center_video_x = min(center_face_x1, center_face_x2) + abs(center_face_x1 - center_face_x2) // 2
#
#         # ------------ drawing bounding rectangle around the detected faces ------------
#         # cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 5)
#         # cv2.circle(frame, (center_face_x1, center_face_y1), 4, (0, 255, 0), -1)
#         #
#         # cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 5)
#         # cv2.circle(frame, (center_face_x2, center_face_y2), 4, (0, 255, 0), -1)
#         #
#         # cv2.circle(frame, (center_video_x, details.VIDEO_HEIGHT // 2), 10, (255, 0, 0), -1)
#
#         cv2.putText(frame, str(face1["confidence"]), (center_face_x1, center_face_y1), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3, cv2.LINE_AA)
#         cv2.putText(frame, str(face2["confidence"]), (center_face_x2, center_face_y2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3, cv2.LINE_AA)
#
#         cv2.imwrite("test.png", frame)
#         if lim_right1 < center_video_x:
#             output_canvas_1 = frame[lim_up1:lim_down1, lim_left1:lim_right1]
#             output_canvas_2 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
#         elif lim_left1 > center_video_x:
#             output_canvas_1 = frame[lim_up2:lim_down2, lim_left2:lim_right2]
#             output_canvas_2 = frame[lim_up1:lim_down1, lim_left1:lim_right1]
#
#         # ------------ adding the ROIs into the 8:9 ratio ------------
#         output_canvas[0:target_height // 2, 0:target_width] = output_canvas_1
#         output_canvas[target_height // 2: target_height, 0:target_width] = output_canvas_2
#
#     # cv2.putText(output_canvas, f"no faces: {str(len(faces))}", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0),
#     #             3, cv2.LINE_AA)
#
#     # ------------ saving the frames into the output video ------------
#     output_video_16x9.write(output_canvas)
#
#     # ------------ showing the image ------------
#     cv2.imshow("frame", output_canvas)
#     if cv2.waitKey(1) == ord("q"):
#         break

input_video.release()
cv2.destroyAllWindows()

# ------------ stopping the timer ------------
end_timer = timer()
print(f"ELAPSED TIME: {end_timer - start_timer}")
