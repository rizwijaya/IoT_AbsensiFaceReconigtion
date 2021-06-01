import tkinter as tk
import tkinter.font as tkFont
import os

class App:
    def __init__(self, root):
        #setting title
        root.title("Sistem Absensi FaceRecognition")
        #setting window size
        width=400
        height=360
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        #Buat button untuk absensi
        GButton_890=tk.Button(root)
        GButton_890["anchor"] = "center"
        GButton_890["bg"] = "#393d49"
        GButton_890["cursor"] = "target"
        GButton_890["disabledforeground"] = "#393d49"
        ft = tkFont.Font(family='Times',size=20)
        GButton_890["font"] = ft
        GButton_890["fg"] = "#ffffff"
        GButton_890["justify"] = "center"
        GButton_890["text"] = "Absen"
        GButton_890["relief"] = "raised"
        GButton_890.place(x=90,y=220,width=218,height=54)
        GButton_890["command"] = self.GButton_890_command
        #Buat button untuk Record Face ID
        GButton_558=tk.Button(root)
        GButton_558["bg"] = "#393d49"
        ft = tkFont.Font(family='Times',size=18)
        GButton_558["font"] = ft
        GButton_558["fg"] = "#ffffff"
        GButton_558["justify"] = "center"
        GButton_558["text"] = "Record Face ID"
        GButton_558.place(x=90,y=130,width=220,height=54)
        GButton_558["command"] = self.GButton_558_command
        #Cetak tittle Murphytech
        GLabel_407=tk.Label(root)
        ft = tkFont.Font(family='Times',size=20)
        GLabel_407["font"] = ft
        GLabel_407["fg"] = "#000000"
        GLabel_407["justify"] = "center"
        GLabel_407["text"] = "Murphytech"
        GLabel_407.place(x=120,y=50,width=150,height=30)

    def GButton_890_command(self):
        print("Lakukan Absensi")
        os.system('python absensi.py')

    def GButton_558_command(self):
        print("Record Face ID Pengguna")
        os.system('python recordface.py')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()