from mtcnn import MTCNN
import cv2


class Detector:
    def __init__(self):
        self.detector = MTCNN()

    def preprocessImage(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 5)

        return blurred

    def returnCenterFaceCoordinates(self, face):
        x, y, w, h = face["box"]

        center_face_x, center_face_y = x + w // 2, y + h // 2

        return center_face_x, center_face_y

    def detectFaces(self, image):
        faces = self.detector.detect_faces(image)

        return faces


class Draw:
    def __init__(self):
        pass

    def drawFace(self):
        pass

    def drawRectangleFaces(self, output_image, face, color=(0, 0, 255), thickness=3):
        """
        Drawing the face detection rectangle on the output frame.
            :param output_image: image on which the drawing should be done
            :param face: coordinates of the face rectangle
            :param color: color of the rectangle; default value: red
            :param thickness: thickness of the rectangle; default value: 3

        :return: image with the face rectangle drawn
        """
        x, y, w, h = face['box']
        cv2.rectangle(output_image, (x, y), (x + w, y + h), color, thickness)

        return output_image
