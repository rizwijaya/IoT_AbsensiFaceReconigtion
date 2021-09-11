from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import time
import cv2
import os
import cv2
from math import pow, sqrt
import simpleaudio as sa

prototxt = "model/SSD_MobileNet_prototxt.txt"
model = "model/SSD_MobileNet.caffemodel"
labels = "model/class_labels.txt"
alarm = "no_mask.wav"
alarm1 = "jagajarak.wav"
jarak = 0.2
face = "face_detector"
model1 = "model/mask_detector.model"
model = "model/SSD_MobileNet.caffemodel"
play_obj = ""
video = ""

def detect_and_predict_mask(frame, faceNet, maskNet):
    # ambil dimensi bingkai dan kemudian buat gumpalan
    # dari itu
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
		(104.0, 177.0, 123.0))

	# lewati gumpalan melalui jaringan dan dapatkan deteksi wajah
	faceNet.setInput(blob)
	detections = faceNet.forward()

	# inisialisasi daftar wajah kami, lokasinya yang sesuai,
    # dan daftar prediksi dari jaringan masker wajah kami
	faces = []
	locs = []
	preds = []

	# ulangi deteksi
	for i in range(0, detections.shape[2]):
        # ekstrak kepercayaan (yaitu, probabilitas) yang terkait dengan
        # deteksi
		confidence = detections[0, 0, i, 2]

        # menyaring deteksi yang lemah dengan memastikan kepercayaannya
        # lebih besar dari kepercayaan minimum
		if confidence > jarak:
        # hitung (x, y)-koordinat kotak pembatas untuk
        # objeknya
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

            # pastikan kotak pembatas berada dalam dimensi bingkai
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

            # ekstrak ROI wajah, ubah dari saluran BGR ke RGB
            # memesan, mengubah ukurannya menjadi 224x224, dan memprosesnya terlebih dahulu
			face = frame[startY:endY, startX:endX]
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (224, 224))
			face = img_to_array(face)
			face = preprocess_input(face)
			face = np.expand_dims(face, axis=0)

            # tambahkan wajah dan kotak pembatas ke masing-masing daftar
			faces.append(face)
			locs.append((startX, startY, endX, endY))

	# hanya membuat prediksi jika setidaknya satu wajah terdeteksi
	if len(faces) > 0:
        # untuk inferensi yang lebih cepat, kami akan membuat prediksi batch di *semua*
        # wajah pada saat yang sama daripada prediksi satu per satu
        # dalam perulangan `untuk` di atas
		preds = maskNet.predict(faces)

    # kembalikan 2-tupel lokasi wajah dan yang sesuai
    # lokasi
	return (locs, preds)

ALARM_ON = False

def sound_alarm(path, play_obj): # mainkan suara alarm
    wave_obj = sa.WaveObject.from_wave_file(path)
    #time.sleep(3) 
    if(play_obj == ""):
        #print('Playing')
        play_obj = wave_obj.play()
        play_obj.wait_done()
    elif(play_obj != ""):
        play_obj.wait_done()
        play_obj = ""
        #print('Ended')

labels = [line.strip() for line in open(labels)]

# Hasilkan kotak pembatas acak bounding_box_color untuk setiap label
bounding_box_color = np.random.uniform(0, 255, size=(len(labels), 3))

print("[INFO] loading face detector model...")

prototxtPath = os.path.sep.join([face, "deploy.prototxt"])
weightsPath = os.path.sep.join([face, "res10_300x300_ssd_iter_140000.caffemodel"])
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# muat model detektor masker wajah dari disk
print("[INFO] loading face mask detector model...")
maskNet = load_model(model1)

# Load model
print("\nLoading model...\n")
network = cv2.dnn.readNetFromCaffe(prototxt, model)

print("\nStreaming video using device...\n")

# Rekam video dari file atau melalui perangkat
if video:
    cap = cv2.VideoCapture(video)
else:
    cap = cv2.VideoCapture(2)
frame_no = 0

while True:
    frame_no = frame_no+1
    ret, frame = cap.read() # Tangkap satu demi satu bingkai
    if not ret: # mendeteksi wajah dalam bingkai dan menentukan apakah mereka mengenakan
        break

    (h, w) = frame.shape[:2] # Ubah ukuran bingkai agar sesuai dengan persyaratan model. Ubah ukuran bingkai menjadi 300X300 piksel
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

    network.setInput(blob)
    detections = network.forward()

    pos_dict = dict()
    coordinates = dict()

    F = 615 # Focal length
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > jarak:
            class_id = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype('int')

            # Memfilter hanya orang yang terdeteksi dalam bingkai. Id Kelas 'orang' adalah 15
            if class_id == 15.00:
                (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)
            	# loop di atas lokasi wajah yang terdeteksi dan yang sesuai lokasi
                for (box, pred) in zip(locs, preds):
            		# membongkar kotak pembatas dan prediksi
                    (startX_mask, startY_mask, endX_mask, endY_mask) = box
                    (mask, withoutMask) = pred
                    # tentukan label kelas dan warna yang akan kita gunakan untuk menggambar
                    # kotak pembatas dan teks
                    if mask > withoutMask:
                        label_mask = "Mask" 
                        color = (0, 255, 0) 
                        ALARM_ON = False
                    else:
                        label_mask="No Mask"
                        color = (0, 0, 255)
                        if not ALARM_ON:
                            ALARM_ON = True
                            if alarm != "":
                                sound_alarm(alarm, play_obj)

                # Gambar kotak pembatas untuk objek
                cv2.rectangle(frame, (startX, startY), (endX, endY), bounding_box_color[class_id], 2)

                label = "{}: {:.2f}%".format(labels[class_id], confidence * 100)
                label_mask = "{}: {:.2f}%".format(label_mask, max(mask, withoutMask) * 100)
                print("{}".format(label))
                cv2.putText(frame, label, (startX_mask, startY_mask - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                cv2.rectangle(frame, (startX_mask, startY_mask), (endX_mask, endY_mask), color, 2)
                coordinates[i] = (startX, startY, endX, endY)

                # Titik tengah kotak pembatas
                x_mid = round((startX+endX)/2,4)
                y_mid = round((startY+endY)/2,4)
                height = round(endY-startY,4)

               # Jarak dari kamera berdasarkan kesamaan segitiga
                distance = (165 * F)/height
                print("Distance(cm):{dist}\n".format(dist=distance))

                # Titik tengah kotak pembatas (dalam cm) berdasarkan teknik kesamaan segitiga
                x_mid_cm = (x_mid * distance) / F
                y_mid_cm = (y_mid * distance) / F
                pos_dict[i] = (x_mid_cm,y_mid_cm,distance)

    # Jarak antara setiap objek yang terdeteksi dalam bingkai
    close_objects = set()
    for i in pos_dict.keys():
        for j in pos_dict.keys():
            if i < j:
                dist = sqrt(pow(pos_dict[i][0]-pos_dict[j][0],2) + pow(pos_dict[i][1]-pos_dict[j][1],2) + pow(pos_dict[i][2]-pos_dict[j][2],2))

                # Periksa apakah jaraknya kurang dari 2 metres atau 200 sentimeter
                if dist < 200:
                    close_objects.add(i)
                    close_objects.add(j)

    for i in pos_dict.keys():
        if i in close_objects:
            COLOR = (0,0,255)
            if not ALARM_ON:
                ALARM_ON = True
                if alarm1 != "":
                    sound_alarm(alarm1, play_obj)
        else:
            COLOR = (0,255,0)
            ALARM_ON = False
        (startX, startY, endX, endY) = coordinates[i]

        cv2.rectangle(frame, (startX, startY), (endX, endY), COLOR, 2)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        # Convert cms to feet
        cv2.putText(frame, 'Depth: {i} ft'.format(i=round(pos_dict[i][2]/30.48,4)), (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR, 2)

    cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)
    # Tampilkan bingkai
    cv2.imshow('Frame', frame)
    cv2.resizeWindow('Frame',800,600)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"): #Tekan `q` untuk keluar
        break

cap.release()
cv2.destroyAllWindows()