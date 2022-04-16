import cv2
import mediapipe as mp
import time
import numpy as np
from io import StringIO
import sys

mp_drawing = mp.solutions.drawing_utils
mp_objectron = mp.solutions.objectron
x_pixel = 640  # 1080
y_pixel = 720  # 720
# For static images:
IMAGE_FILES = []
with mp_objectron.Objectron(static_image_mode=True,
                            max_num_objects=1,
                            min_detection_confidence=0.4,
                            model_name='Cup') as objectron:
    for idx, file in enumerate(IMAGE_FILES):
        image = cv2.imread(file)
        # Convert the BGR image to RGB and process it with MediaPipe Objectron.
        results = objectron.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Draw box landmarks.
        if not results.detected_objects:
            print(f'No box landmarks detected on {file}')
            continue
        print(f'Box landmarks of {file}:')
        annotated_image = image.copy()
        for detected_object in results.detected_objects:
            mp_drawing.draw_landmarks(
                annotated_image, detected_object.landmarks_2d, mp_objectron.BOX_CONNECTIONS)
            mp_drawing.draw_axis(annotated_image, detected_object.rotation,
                                 detected_object.translation)
            cv2.imwrite('/tmp/annotated_image' +
                        str(idx) + '.png', annotated_image)

# 轉換座標


def pixel(x_ndc, y_ndc, image_width, image_height):
    x_pixel = (1 + x_ndc) / 2.0 * image_width
    y_pixel = (1 - y_ndc) / 2.0 * image_height
    return x_pixel, y_pixel


# For webcam input:
cap = cv2.VideoCapture(0)

# 取得影像長寬
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(width, height)


with mp_objectron.Objectron(static_image_mode=True,
                            max_num_objects=5,
                            min_detection_confidence=0.3,
                            min_tracking_confidence=0.3,
                            model_name='Cup') as objectron:
    while cap.isOpened():
        success, image = cap.read()
        start = time.time()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = objectron.process(image)

        # Draw the box landmarks on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        keypoints = []
        if results.detected_objects:
            for detected_object in results.detected_objects:
                mp_drawing.draw_landmarks(
                    image, detected_object.landmarks_2d, mp_objectron.BOX_CONNECTIONS)
                mp_drawing.draw_axis(image, detected_object.rotation,
                                     detected_object.translation)

                cx = detected_object.landmarks_3d.landmark[1].x
                cy = detected_object.landmarks_3d.landmark[1].y
                cz = detected_object.landmarks_3d.landmark[0].z
                Distance = (cz+1)/2
                print("Distance=", (int)(Distance*100), "cm")

                x_pixel, y_pixel = pixel(cx, cy, width, height)
                x_pixel = int(x_pixel)
                y_pixel = int(y_pixel*1.25)
                #print("x=", x_pixel, "y=", y_pixel)

                # print("scale", detected_object.scale,
                #      "rotation", detected_object.rotation)

        # Flip the image horizontally for a selfie-view display.

        end = time.time()
        totalTime = end-start
        fps = 1/totalTime
        cv2.putText(image, f'FPS:{int(fps)}', (20, 70),
                    cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 2)

        cv2.line(image, (x_pixel, y_pixel),
                 (int(width/2), int(height)), (0, 0, 255), 5)
        cv2.circle(image, (x_pixel, y_pixel), 20, (0, 0, 255), 5)
        cv2.imshow('MediaPipe Objectron', image)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite('output.jpg', image)
        # cv2.imshow('MediaPipe Objectron', cv2.flip(image, 1))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()
