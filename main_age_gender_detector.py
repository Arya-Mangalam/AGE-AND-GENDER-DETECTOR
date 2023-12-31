#code by arya
import cv2

# Face detection model
faceProto = "opencv_face_detector.pbtxt"
faceModel = "opencv_face_detector_uint8.pb"

# Age model
ageProto = "age_deploy.prototxt"
ageModel = "age_net.caffemodel"

# Gender model
genderProto = "gender_deploy.prototxt"
genderModel = "gender_net.caffemodel"

# Function to create face box
def faceBox(faceNet, frame):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (227, 227), [104, 117, 123], swapRB=False)
    faceNet.setInput(blob)
    detection = faceNet.forward()
    bbox = []

    for i in range(detection.shape[2]):
        con = detection[0, 0, i, 2]
        if con > 0.7:
            x1 = int(detection[0, 0, i, 3] * frameWidth)
            y1 = int(detection[0, 0, i, 4] * frameHeight)
            x2 = int(detection[0, 0, i, 5] * frameWidth)
            y2 = int(detection[0, 0, i, 6] * frameHeight)
            bbox.append([x1, y1, x2, y2])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

    return frame, bbox

# Load pre-trained models
faceNet = cv2.dnn.readNet(faceModel, faceProto)
ageNet = cv2.dnn.readNet(ageModel, ageProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)

# Constants and lists
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(20-30)', '(32-44)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

# Capture video from the default camera
video = cv2.VideoCapture(0)
padding = 20

while True:
    ret, frame = video.read()
    frame, bboxs = faceBox(faceNet, frame)

    for bbox in bboxs:
        face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
                     max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]
        blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

        genderNet.setInput(blob)
        genderPred = genderNet.forward()
        gender = genderList[genderPred[0].argmax()]

        ageNet.setInput(blob)
        agePred = ageNet.forward()
        age = ageList[agePred[0].argmax()]

        label = "{},{}".format(gender, age)
        cv2.putText(frame, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("age-gender", frame)
    k = cv2.waitKey(1)
    if k==27 or k == ord('q'):
        break

# Release video capture and close windows
video.release()
cv2.destroyAllWindows()
