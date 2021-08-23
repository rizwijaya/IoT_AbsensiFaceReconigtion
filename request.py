import requests
from requests.api import request
from requests.structures import CaseInsensitiveDict
import subprocess
from datetime import datetime

webservice = "http://localhost:81/WebService/api/"
bearer = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjIiLCJ1c2VybmFtZSI6InJpenFpIiwiaWF0IjoxNjI5NTM3NzA3LCJleHAiOjE2MzEzMzc3MDd9.fYeKQ4RVCUsvyR5-NogaVKVXJmc9V9CrPLxlOzR7NXE"

def getdevice():
    url = webservice + "request/cekdevice?device=1"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer

    resp = requests.get(url, headers=headers)
    return resp

def updateServer(id):
    url = webservice + "request/updatestatus"
    myobj = {'id' : id}
    
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = bearer

    x = requests.post(url, data=myobj, headers=headers)
    return x.text

def main():
    i = 0
    while True:
        r = getdevice()
        now = datetime.now()
        if(r.status_code == 200):
            #print(r.json())
            if(r.json()['end_run'] == now.strftime("%Y-%m-%d %H:%M:%S")): #Mematikan perangkat otomatis
                x = updateServer(int(r.json()['id_running']))
                print(x)
                print("Proses pada perangkat dihentikan2")
            elif(r.json()['sts_running'] == '1' and r.json()['sts_command'] == '1'):
                if(i == 0 and r.json()['mulai_run'] == now.strftime("%Y-%m-%d %H:%M:%S")): #Jika jam dan waktu sesuai dengan yang ditentukan
                    print("Menjalankan system Absensi")
                    absen = subprocess.Popen(["python", "absensi.py"])
                    i = 1
            elif(r.json()['sts_running'] == '1' and r.json()['sts_command'] == '2'):
                if(i == 0 and r.json()['mulai_run'] == now.strftime("%Y-%m-%d %H:%M:%S")):
                    print("Menjalankan Face Record")
                    face = subprocess.Popen(["python", "recordface.py"])
                    i = 2
            elif(r.json()['sts_running'] == '2'): #Jika dimatikan manual
                if(i == 1):
                    i = 0
                    absen.terminate()
                elif(i == 2):
                    i = 0
                    face.terminate()
                print("Proses pada perangkat dihentikan")
            else:
                print("Tidak ada kelas")
        else:
            if(i == 1):
                i = 0
                absen.terminate()
                print("Proses pada perangkat dihentikan")
            elif(i == 2):
                i = 0
                face.terminate()
                print("Proses pada perangkat dihentikan")
            print("Tidak ada absensi")

if __name__ == "__main__":
    main()