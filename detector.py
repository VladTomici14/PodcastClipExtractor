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

    def sortArr(self, arr, output_arr):
        for i in range(len(arr)):
            if i > 0 and i <= len(arr):
                if arr[i] == 0 and arr[i-1] != 0:
                    arr[i] = arr[i - 1]
                    output_arr[i] = output_arr[i-1]

                if arr[i] == 0 and arr[i-1] == 0:
                    arr[i] = 1

                if arr[i] != arr[i - 1] and arr[i - 1] == arr[i + 1]:
                    arr[i] = arr[i - 1]
                    output_arr[i] = output_arr[i-1]

        return arr, output_arr

    def secondSorter(self, arr):
        """
        :param arr:
        :return:
        """
        current_element = arr[0]
        k = 0
        subarr = []
        values = []
        subarr.append(current_element)
        for i in range(len(arr)):
            if i > 0:
                if arr[i] == current_element:
                    subarr.append(arr[i])
                else:
                    values.append(subarr)
                    subarr = []
                    current_element = arr[i]
                    subarr.append(current_element)

        values.append(subarr)

        for elem in values:
            print(elem)

        for i in range(len(values)):
            if 0 < i < len(values)-1:
                left_arr = values[i-1]
                right_arr = values[i+1]
                if len(values[i]) <= 15 and left_arr[0] == right_arr[0]: # FIXME: problems with 0 values
                    print("da")
                    self.transformArray(values[i], left_arr[0])

        fin_values = []
        for i in range(len(values)):
            print(i)
            print(f"subarr{i}: {values[i]}")
            for element in values[i]:
                fin_values.append(element)

        print(f"TOTAL OF VALUES: {len(fin_values)}")

        return fin_values

    def transformArray(self, arr, value):
        for i in range(len(arr)):
            arr[i] = value

        return arr

    # def secondSort(self, arr, output_arr):
    #     k = 0
    #     for i in range(len(arr)):
    #         if i > 0 and i <= len(arr):
    #             if arr[i] == arr[i-1]:
    #                 k += 1
    #             else:
    #                 if k <= 15:
    #                     for j in range()

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
