# Import the neccesary libraries
import numpy as np
import argparse
import cv2
import time
import mraa

KNOWN_DISTANCE = 45  # INCHES
PERSON_WIDTH = 16  # INCHES
MOBILE_WIDTH = 3.0  # INCHES
BOTTLE_WIDTH = 4.0  # INCHES
# Object detector constant
CONFIDENCE_THRESHOLD = 0.4
NMS_THRESHOLD = 0.3
# Webcame的解析度
x_pixel = 1280  # 640
y_pixel = 720  # 720


# construct the argument parse
parser = argparse.ArgumentParser(
    description='Script to run MobileNet-SSD object detection network ')
parser.add_argument(
    "--video", help="path to video file. If empty, camera's stream will be used")
parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt",
                    help='Path to text network file: '
                    'MobileNetSSD_deploy.prototxt for Caffe model or '
                    )
parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel",
                    help='Path to weights: '
                    'MobileNetSSD_deploy.caffemodel for Caffe model or '
                    )
parser.add_argument("--thr", default=0.2, type=float,
                    help="confidence threshold to filter out weak detections")
args = parser.parse_args()

# Labels of Network.
classNames = {0: 'background',
              1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
              5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
              10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
              14: 'motorbike', 15: 'person', 16: 'pottedplant',
              17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor'}

# Open video file or capture device.
if args.video:
    cap = cv2.VideoCapture(0)  #
else:
    cap = cv2.VideoCapture('../IMG_0608.mov')
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    out = cv2.VideoWriter('output99.mp4', fourcc, 20.0, (640, 360))
print(width, height)
#fps = int(cap.get(cv2.CAP_PROP_FPS))

# Load the Caffe model
net = cv2.dnn.readNetFromCaffe(args.prototxt, args.weights)

# assign gpios
ain1=mraa.Gpio(107,owner=False,raw=True)
ain2=mraa.Gpio(108,owner=False,raw=True)
nsleep1=mraa.Gpio(111,owner=False,raw=True)
bin1=mraa.Gpio(171,owner=False,raw=True)
bin2=mraa.Gpio(172,owner=False,raw=True)
nsleep2=mraa.Gpio(175,owner=False,raw=True)
# set gpio direction
ain1.dir(mraa.DIR_OUT)
ain2.dir(mraa.DIR_OUT)
nsleep1.dir(mraa.DIR_OUT)
bin1.dir(mraa.DIR_OUT)
bin2.dir(mraa.DIR_OUT)
nsleep2.dir(mraa.DIR_OUT)
# set initial gpio value
ain1.write(1)
ain2.write(0)
nsleep1.write(1)
bin1.write(0)
bin2.write(1)
nsleep2.write(1)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    start = time.time()
    # resize frame for prediction
    frame_resized = cv2.resize(frame, (300, 300))

    # MobileNet requires fixed dimensions for input image(s)
    # so we have to ensure that it is resized to 300x300 pixels.
    # set a scale factor to image because network the objects has differents size.
    # We perform a mean subtraction (127.5, 127.5, 127.5) to normalize the input;
    # after executing this command our "blob" now has the shape:
    # (1, 3, 300, 300)
    blob = cv2.dnn.blobFromImage(
        frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    # Set to network the input blob
    net.setInput(blob)
    # Prediction of network
    detections = net.forward()

    # Size of frame resize (300x300)
    cols = frame_resized.shape[1]
    rows = frame_resized.shape[0]

    # For get the class and location of object detected,
    # There is a fix index for class, location and confidence
    # value in @detections array .
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]  # Confidence of prediction
        if confidence > args.thr:  # Filter prediction
            class_id = int(detections[0, 0, i, 1])  # Class label

            # Object location
            xLeftBottom = int(detections[0, 0, i, 3] * cols)
            yLeftBottom = int(detections[0, 0, i, 4] * rows)
            xRightTop = int(detections[0, 0, i, 5] * cols)
            yRightTop = int(detections[0, 0, i, 6] * rows)

            # Factor for scale to original size of frame
            heightFactor = frame.shape[0]/300.0
            widthFactor = frame.shape[1]/300.0
            # Scale object detection to frame
            xLeftBottom = int(widthFactor * xLeftBottom)
            yLeftBottom = int(heightFactor * yLeftBottom)
            xRightTop = int(widthFactor * xRightTop)
            yRightTop = int(heightFactor * yRightTop)
            # Draw location of object
            cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
                          (0, 255, 0))

            # Draw label and confidence of prediction in frame resized
            if class_id in classNames:
                if class_id == 5:  # bottle的id
                    label = classNames[class_id] + ": " + str(confidence)
                    labelSize, baseLine = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                    yLeftBottom = max(yLeftBottom, labelSize[1])
                    cv2.rectangle(frame, (xLeftBottom, yLeftBottom - labelSize[1]),
                                  (xLeftBottom + labelSize[0],
                                   yLeftBottom + baseLine),
                                  (255, 255, 255), cv2.FILLED)
                    cv2.putText(frame, label, (xLeftBottom, yLeftBottom),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                    #print(xLeftBottom, yLeftBottom)
                    cv2.line(frame, (xLeftBottom, yLeftBottom),
                             (int(width*0.4), int(height)), (0, 0, 255), 5)
                    cv2.line(frame, (xRightTop, yLeftBottom),
                             (int(width*0.6), int(height)), (0, 0, 255), 5)
                    center = [(xLeftBottom+xRightTop)/2,
                              (yLeftBottom+yRightTop)/2]
                    #xLeftBottom, xRightTopy, LeftBottom, yRightTop, center分別為bottle的左上右下座標與中心點

                    cv2.circle(frame, (int(center[0]), int(
                        center[1])), 38, (0, 0, 225), -1)
                    # 畫出中心點

                    if center[0]<=(width/3):
                        ain1.write(0)
                        ain2.write(1)
                        bin1.write(1)
                        bin2.write(0)
                        nsleep2.write(1)
                        if center[1]>(height*2/3):
                            nsleep1.write(1)
                        else:
                            nsleep1.write(0)
                    elif center[0]>(width*2/3):
                        ain1.write(1)
                        ain2.write(0)
                        bin1.write(0)
                        bin2.write(1)
                        nsleep1.write(1)
                        if center[1]>(height*2/3):
                            nsleep2.write(1)
                        else:
                            nsleep2.write(0)
                    else:
                        ain1.write(1)
                        ain2.write(0)
                        bin1.write(1)
                        bin2.write(0)
                        nsleep1.write(1)
                        nsleep2.write(1)


                # print(label)  # print class and confidence

                cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                end = time.time()
                totalTime = end-start
                fps = 1/totalTime
                cv2.putText(frame, f'FPS:{float(fps)}', (20, 70),
                            cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 2)
                out.write(frame)
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) >= 0:  # Break with ESC
        break
