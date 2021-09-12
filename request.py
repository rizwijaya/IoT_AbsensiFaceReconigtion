import requests
from requests.api import request
from requests.structures import CaseInsensitiveDict
import subprocess
from datetime import datetime
import os

# webservice = "http://localhost:81/WebService/api/"
# bearer = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJ1c2VybmFtZSI6InJpenFpIiwiaWF0IjoxNjMxMzM0ODc2LCJleHAiOjE2MzMxMzQ4NzZ9.YkHir7WyKAlKJZwf6TeYB3-eIVBGiKqFgU9IAdZrNy4"
webservice = "http://ludaringin.tech/api/"
bearer = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJ1c2VybmFtZSI6InJpenFpIiwiaWF0IjoxNjMxNDEyMjg0LCJleHAiOjE2MzMyMTIyODR9.BqtrZeb59_L08fg_b3cDR-DVjIPLZ1wAR2R5K2v7dwg"
device = 1

def resetPintu():
    url = webservice + "request/resetpintu?device=" + str(device)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    #headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    headers["User-Agent"] = 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.187 Safari/537.36' #Raspberry 

    resp = requests.get(url, headers=headers)
    return resp

def getdevice():
    url = webservice + "request/cekdevice?device=" + str(device)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    #headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36' # windows
    headers["User-Agent"] = 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.187 Safari/537.36' #Raspberry 

    resp = requests.get(url, headers=headers)
    return resp

def updateServer(id):
    url = webservice + "request/updatestatus"
    myobj = {'id' : id}
    
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    #headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    headers["User-Agent"] = 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.187 Safari/537.36' #Raspberry 

    x = requests.post(url, data=myobj, headers=headers)
    return x.text

def getMatkul(pertemuan):
    url = webservice + "request/getmatkul?pertemuan=" + pertemuan

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    #headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36' # windows
    headers["User-Agent"] = 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.187 Safari/537.36' #Raspberry 

    resp = requests.get(url, headers=headers)
    return resp

def cekPintu():
    url = webservice + "request/cekpintu?device=" + str(device)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    #headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36' # windows
    headers["User-Agent"] = 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.187 Safari/537.36' #Raspberry 

    resp = requests.get(url, headers=headers)
    return resp

def resetPintu():
    url = webservice + "request/resetpintu"
    myobj = {'device' : str(device)}
    
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer
    #headers["User-Agent"] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    headers["User-Agent"] = 'Mozilla/5.0 (X11; CrOS armv7l 13597.84.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.187 Safari/537.36' #Raspberry 
    x = requests.post(url, data=myobj, headers=headers)
    return x.text

def main():
    i = 0
    #Full Screen Mode
    #os.system("python fullscreen.py") #windows
    #os.system("python3 fullscreen.py") #rasp
    layar = subprocess.Popen(["python3", "fullscreen.py"])
    #Jalankan Mask detectionnya.
    #os.system("python mask_alert.py") #windows
    #os.system("python3 mask_alert.py") #rasp
    maskdetection = subprocess.Popen(["python3", "mask_alert.py"]) #raspberry
    #Lakukan request
    while True:
        r = getdevice()
        reset = cekPintu()
        now = datetime.now()
        #if(reset.json()['status'] != False):
        if(reset.json()['bukapintu'] == 1):
            dataMatkul = getMatkul(r.json()['id_pertemuan'])
            if(dataMatkul.json()['end_kuliah'] == now.strftime("%Y-%m-%d %H:%M:%S")):
                resetPintu() #Kirimkan request reset bukapintu
                print("Melakukan reset Data")
            else:
                print("Tidak direset")
        if(r.status_code == 200):
            #print(r.json())
            if(r.json()['end_run'] == now.strftime("%Y-%m-%d %H:%M:%S")): #Mematikan perangkat otomatis
                x = updateServer(int(r.json()['id_running']))
                print(x)
                print("Proses pada perangkat dihentikan2")
            elif(r.json()['sts_running'] == '1' and r.json()['sts_command'] == '1'):
                if(i == 0 and r.json()['mulai_run'] == now.strftime("%Y-%m-%d %H:%M:%S")): #Jika jam dan waktu sesuai dengan yang ditentukan
                    print("Menjalankan system Absensi")
                    layar.terminate()
                    #absen = subprocess.Popen(["python", "absensi.py"]) # windows
                    absen = subprocess.Popen(["python3", "absensi.py"]) #raspberry pi
                    i = 1
            elif(r.json()['sts_running'] == '1' and r.json()['sts_command'] == '2'):
                if(i == 0 and r.json()['mulai_run'] == now.strftime("%Y-%m-%d %H:%M:%S")):
                    print("Menjalankan Face Record")
                    layar.terminate()
                    #face = subprocess.Popen(["python", "recordface.py"]) # windows
                    face = subprocess.Popen(["python3", "recordface.py"]) # raspberry pi
                    i = 2
            elif(r.json()['sts_running'] == '2'): #Jika dimatikan manual
                if(i == 1):
                    i = 0
                    absen.terminate()
                    layar = subprocess.Popen(["python3", "fullscreen.py"])
                elif(i == 2):
                    i = 0
                    face.terminate()
                    layar = subprocess.Popen(["python3", "fullscreen.py"])
                print("Proses pada perangkat dihentikan")
            else:
                print("Tidak ada kelas")
        else:
            if(i == 1):
                i = 0
                absen.terminate()
                layar = subprocess.Popen(["python3", "fullscreen.py"])
                print("Proses pada perangkat dihentikan")
            elif(i == 2):
                i = 0
                face.terminate()
                layar = subprocess.Popen(["python3", "fullscreen.py"])
                print("Proses pada perangkat dihentikan")
            print("Tidak ada absensi")

if __name__ == "__main__":
    main()
