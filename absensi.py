import cv2
import numpy as np
import os
import pandas as pd
from matplotlib import pyplot as plt
import time
import datetime
import requests
from requests.api import request
from requests.structures import CaseInsensitiveDict
from smbus2 import SMBus
from mlx90614 import MLX90614
import subprocess

webservice = "http://ludaringin.tech/api/"
bearer = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJ1c2VybmFtZSI6InJpenFpIiwiaWF0IjoxNjI5OTAwNzQ4LCJleHAiOjE2MzE3MDA3NDh9.-gttj3xEOu1GkRXCspoPa7q1ws-uXlqpPLRAlIZahE0"

def deteksiSuhu():
    bus = SMBus(1)
    sensor = MLX90614(bus, address=0x5A)
    suhuSekitar = sensor.get_ambient()
    suhuObyek = sensor.get_object_1()
    if suhuObyek < 37:
      bukaPintu  = subprocess.Popen(["python", "solenoid.py"]) # sesuaikan versi python
      hasil = 1
    else :
        hasil = 0
    bus.close()
    return hasil
    
def getPertemuan():
    url = webservice + "request/getpertemuan?device=1"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

    resp = requests.get(url, headers=headers)
    return resp

def updateKehadiran(nama): 
    r = getPertemuan()
    url = webservice + "request/hadir"
    myobj = {
        'nama' : str(nama),
        'pertemuan' : r.json()['id_pertemuan']
    }

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

    x = requests.post(url, data=myobj, headers=headers)
    return x

#SetUp Port Kameranya
portCamera = 0

# images properties
def plt_show(image, title=""):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.axis("off")
    plt.title(title)
    plt.imshow(image, cmap="Greys_r")
    plt.show()

# face detection    
class FaceDetector(object):
    def __init__(self, xml_path):
        self.classifier = cv2.CascadeClassifier(xml_path)
    
    def detect(self, image, biggest_only=True):
        scale_factor = 1.2
        min_neighbors = 5
        min_size = (75, 75)
        biggest_only = True
        flags = cv2.CASCADE_FIND_BIGGEST_OBJECT |                     cv2.CASCADE_DO_ROUGH_SEARCH if biggest_only else                     cv2.CASCADE_SCALE_IMAGE
        faces_coord = self.classifier.detectMultiScale(image,
                                                       scaleFactor=scale_factor,
                                                       minNeighbors=min_neighbors,
                                                       minSize=min_size,
                                                       flags=flags)
        return faces_coord

# video camera
class VideoCamera(object):
    def __init__(self, index=portCamera):
        #self.video = cv2.VideoCapture(index) #Raspberry Mode
        self.video = cv2.VideoCapture(index, cv2.CAP_DSHOW) #Untuk Pengembangan
        self.index = index
        print (self.video.isOpened())

    def __del__(self):
        self.video.release()
    
    def get_frame(self, in_grayscale=False):
        _, frame = self.video.read()
        if in_grayscale:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

# crop images
def cut_faces(image, faces_coord):
    faces = []
    
    for (x, y, w, h) in faces_coord:
        w_rm = int(0.3 * w / 2)
        faces.append(image[y: y + h, x + w_rm: x + w - w_rm])
         
    return faces

# normalize images
def normalize_intensity(images):
    images_norm = []
    for image in images:
        is_color = len(image.shape) == 3 
        if is_color:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        images_norm.append(cv2.equalizeHist(image)) #Menyesuaikan kontrass menggunakan histogram citra
    return images_norm

# resize images
def resize(images, size=(100, 100)):
    images_norm = []
    for image in images:
        if image.shape < size:
            image_norm = cv2.resize(image, size, 
                                    interpolation=cv2.INTER_AREA)
        else:
            image_norm = cv2.resize(image, size, 
                                    interpolation=cv2.INTER_CUBIC)
        images_norm.append(image_norm)

    return images_norm

# normalize faces
def normalize_faces(frame, faces_coord):
    faces = cut_faces(frame, faces_coord)
    faces = normalize_intensity(faces)
    faces = resize(faces)
    return faces

# rectangle line
def draw_rectangle(image, coords):
    for (x, y, w, h) in coords:
        w_rm = int(0.2 * w / 2) 
        cv2.rectangle(image, (x + w_rm, y), (x + w - w_rm, y + h), 
                              (102, 255, 0), 1)

# dapatkan gambar dari kumpulan data
def collect_dataset():
    images = []
    labels = []
    labels_dic = {}
    members = [person for person in os.listdir("siswa/")]
    for i, person in enumerate(members):   # loop over
        labels_dic[i] = person
        for image in os.listdir("siswa/" + person):
            images.append(cv2.imread("siswa/" + person + '/' + image, 
                                     0))
            labels.append(i)
    return (images, np.array(labels), labels_dic)

images, labels, labels_dic = collect_dataset()


# train image (algorithm sets)
rec_eig = cv2.face.EigenFaceRecognizer_create()
rec_eig.train(images, labels)

rec_fisher = cv2.face.FisherFaceRecognizer_create()
rec_fisher.train(images, labels)

rec_lbph = cv2.face.LBPHFaceRecognizer_create()
rec_lbph.train(images, labels)

print ("Models Trained Berhasil")


# cascade face and mask
detector = FaceDetector("xml/frontal_face.xml")
detector_mask = cv2.CascadeClassifier("xml/mask_cascade.xml")

# 0 usb webcam additional
webcam = VideoCamera(portCamera)


ts = time.time()      
date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
label2 = ""
# mask detection and face recognition
while True: 
    #Cek Penggunaan Masker
    frame1 = webcam.get_frame()
    mask = detector_mask.detectMultiScale(frame1, 
                                 scaleFactor=1.2, 
                                 minNeighbors=5, 
                                 minSize=(100, 100),
                                 maxSize=(150, 150),
                                 flags=cv2.CASCADE_SCALE_IMAGE)
    for(x1,y1,x2,y2) in mask:
        cv2.rectangle(frame1,(x1,y1),(x1+x2,y1+y2),(0,255,0),2)
        cv2.putText(frame1, 'Pakai Masker',(x1, y1+y2 + 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,255,255), 2)
        cv2.putText(frame1, "Selanjutnya Wajah", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_4)
     
    faces_coord = detector.detect(frame1, False) #deteksi lebih dari satu wajah
    col_names =  ['Nama','Tgl','Jam']
    attendance = pd.DataFrame(columns = col_names)

    #Cek Face Recognition
    if len(faces_coord):
        faces = normalize_faces(frame1, faces_coord) # norm pipeline
        for i, face in enumerate(faces): # untuk setiap wajah yang terdeteksi
            collector = cv2.face.StandardCollector_create()
            rec_lbph.predict_collect(face, collector)  # algoritma yang dipilih
            conf = collector.getMinDist()
            pred = collector.getMinLabel()
            threshold = 76 # eigen, fisher, lbph [mean 3375,1175,65] [high lbph 76]
            print ("Nama: " + labels_dic[pred].capitalize() + "\nSkala Prediksi: " + str(round(conf)))
            
            if conf < threshold: # menerapkan ambang batas
                cv2.putText(frame1, labels_dic[pred].capitalize(),
                            (faces_coord[i][0], faces_coord[i][1] - 20),
                            cv2.FONT_HERSHEY_DUPLEX, 1.0, (102, 255, 0), 1)
                attendance.loc[len(attendance)] = [labels_dic[pred],date,timeStamp]
                if(label2 != labels_dic[pred]): #Letak program cek suhu pengguna nya.
                    suhu = deteksiSuhu(labels_dic[pred])
                    if suhu == 1: #Diperbolehkan masuk
                        x = updateKehadiran(labels_dic[pred])
                        displaySuhu = x.json()['message']
                    elif suhu == 0: #Jika suhu tidak terpenuhi
                        displaySuhu = "Anda dalam kategori tidak fit, tidak diperkenankan masuk"
                label2 = labels_dic[pred]
                cv2.putText(frame1, displaySuhu, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_4)
                #print(x.text)
            else:
                cv2.putText(frame1, "Tidak Dikenali",
                    (faces_coord[i][0], faces_coord[i][1] - 10),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (66, 55, 245), 1)
        draw_rectangle(frame1, faces_coord) # rectangle around face
    cv2.putText(frame1, "ESC to exit", (5, frame1.shape[0] - 5),
    cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imshow("Sistem Absensi Face Recognitions", frame1) # live feed in external
    if cv2.waitKey(33) & 0xFF == 27:
        cv2.destroyAllWindows()
        break

del webcam
