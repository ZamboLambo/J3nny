from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import requests
import threading
from time import sleep
from datetime import *

from base64 import b64decode
from PIL import Image
from io import BytesIO
from os import remove

def makeEntry(lname, master, infoText):
    lPat = ttk.Label(master, text=lname)
    lPat.grid()
    tButton = ttk.Button(master, text="?", command= lambda: showinfo("Input info",infoText), width=1)
    Button.grid(self=tButton, column=1, row=lPat.grid_info()['row'])
    tEntry = Entry(master, exportselection=0, disabledbackground="light gray", disabledforeground="black")
    tEntry.grid(padx=20, pady=5)
    return tEntry


class Gui:
    #all needed outside class should be to properly init and call run()

    def __init__(self, backFunction):
        #only input: function to be used on the loop
        self.window = Tk()
        self.window.resizable(False, False)

        #b64 stupid hack needed to make a onefile with images all in it
        temp = Image.open(BytesIO(b64decode("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"
        )))
        temp.thumbnail((30,30),Image.ANTIALIAS)
        temp.save("start.png")
        self.startIco = PhotoImage(file="start.png")
        remove("start.png")

        temp = Image.open(BytesIO(b64decode("iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAABbmlDQ1BpY2MAACiRdZHPKwRhGMc/Bq1YOZCEw6ZdOVCi5Mg67GWTFmVx2R0zu2p3dprZTZurcnHYchAXvw7+A67KlVKKlOTo7NdFGs9r1Uq77/TO8+n7vt+nZ74DWjSjZ92GCchaeScWCQcW4osB3zMaPXQSoi+hu/bkzEyUmuvjljpVb4ZUr9r3qq6WFcPVoa5JeEy3nbywTEN0LW8r3hLu0NOJFeED4UFHBhS+VHqyzE+KU2V+U+zMxaZAUz0DqT+c/MN62skKDwgHs5mC/juP+hK/Yc3PSu2W3YtLjAhhAiQpsEqGPENSLcmsum/4xzdNTjy6vG2KOOJIkRbvoKgF6WpINUU35MlQVLn/z9M1R0fK3f1haHz0vNcQ+Lbhq+R5n4ee93UE9Q9wblX8Oclp/F30UkUL7kPbBpxeVLTkDpxtQte9nXASP1K9bM004eUEWuPQfg3NS+Wsfs85voO5dflFV7C7B/1yv235Gz5SaCYC2B3kAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAB8UlEQVR4Xu3cvy4EYRSG8eNPrUAjCkSp0KjdgrgHiU4icQUacRsiUSs0GpVEQUMhKo2OBBVBcE7WZuXbsDv7zcg79vklbzObWbMeq/zMAAAAAAAAAAAAAAB9Yti34bvyvfreC+zOt+ebsXwDvlXfhe/F2n/Wb7v37fvm7B/Y9H18Lf2gnda879w3bnnWrPV+RZ+lec+1b8pq7tGK/wLSxf3r1rtR342V8xzbVrHB9ELJRqzxQXItpBcKmPZNWP5zxP0r6cWyVR2kLEPphQLK/IzxbatUmQ/bD3K/ZR0RRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxBBEDEHEEEQMQcQQRAxBxNQlSJy726u4N+f+78p6nx9VHaSsMwpv0wsFPPieLf+XGfcfpRfr5sTyzsuNe998i9a7ONH0wPKfI7ZkNTfvu7TWByq6J2scVZ5r1ndq7e/f7eKY9C2r/j9K9te4G3FM+LI1zl4fs8ZfXCfxXHHe+q7vLHmtV3Goc/yFx3NMWnfPEQEOfTu+4+Q1AAAAAAAAAAAAAADwhz4B9aO7n4H551UAAAAASUVORK5CYII="       
        )))
        temp.thumbnail((30,30),Image.ANTIALIAS)
        temp.save("stop.png")
        self.stopIco = PhotoImage(file="stop.png")
        remove("stop.png")
        


        self.frm = ttk.Frame(self.window, padding=10,)
        self.frm.grid()

        self.threadPat = makeEntry("Thread pattern", self.frm, 
"A word or sentence present in the thread OP to be searched, must be unique. ie: Nominations"),

        self.board = makeEntry("Board",  self.frm, 
        "Letter or word of the board to scrape. ie: v, a, trash"),

        self.sheet = makeEntry("Google Sheet", self.frm,
"Name of Google Sheets sheet to use/override, if inexistent it will be created. Uneeded if Google Sheets isn't set to be used."),

        self.minRep = makeEntry("Minimum replies", self.frm,
        "Minimum replies for a nomination to be considered valid."),

        self.almo = makeEntry("itsalmo.st", self.frm, 
        "Link of the itsalmo.st timer to use. Part after the / only.")


        self.startButton = ttk.Button(self.frm, image=self.startIco, command=lambda: self.validateRun(lambda: backFunction()))
        self.startButton.grid(padx=20, pady=5)



    def validateRun(self, func):
        # if(
        #     requests.get(
        #         "https://boards.4chan.org/" + self.board[0].get() +"/catalog"
        #     ).status_code == 404
        # ):
        #     showerror("Invalid input", "Invalid board.")
        #     self.board[0].config({"background": "Pink"})
        #     return False
        # if(
        #     requests.get(
        #         "https://itsalmo.st/" + self.almo.get()
        #     ).status_code == 404
        # ):
        #     showerror("Invalid input", "Invalid almo.st link.")
        #     self.almo.config({"background": "Pink"})
        #     return False

        #for some reason all but almo got returned as a lenght 1 tuple...
        self.almo["state"] = 'disabled'
        self.minRep[0]["state"] = 'disabled'
        self.sheet[0]["state"] = 'disabled'
        self.board[0]["state"] = 'disabled'
        self.threadPat[0]["state"] = 'disabled'

        self.startButton.destroy()

        newfrm = ttk.Frame(self.window, padding=10)
        self.paused = BooleanVar(value=False)

        newfrm.grid()
        self.buttonPause = ttk.Button(newfrm, command=self.pause, image=self.stopIco)
        self.buttonPause.grid()

        self.end = datetime.now() + timedelta(hours=1)

        self.stateInfo = ttk.Label(newfrm, text="I AM ERROR", background="black",
         foreground="green2", padding=10)
        self.stateInfo.grid()
        self.lock = threading.Lock()

        thread = threading.Thread(target=lambda: self.doWork(func), daemon=True)
        thread.start()
        
        timerThread = threading.Thread(target=self.updateState, daemon=True)
        timerThread.start()

    def updateState(self):
        while datetime.now() < self.end:
            left = self.end - datetime.now()
            self.stateInfo.configure(text=str(left).rpartition('.')[0])
            sleep(1) # no need to update every microsecond if we're ignoring those
        self.stateInfo.configure(text="OVER", foreground="red")

    def doWork(self, func):
        x = func()
        while datetime.now() < self.end:
            
            self.pauseTimer(x)
            x = func()


    def pause(self):
        if self.paused.get():
            self.buttonPause.configure(image=self.stopIco)
            self.lock.release()
        else:
            self.buttonPause.configure(image=self.startIco)

        self.paused.set(not(self.paused.get()))

    def pauseTimer(self, secs):

            while secs:

                if self.paused.get():
                    self.stateInfo.configure(foreground="red")
                    self.lock.acquire()
                    self.stateInfo.configure(foreground="green2")
                sleep(0.25)
                secs = secs - 0.25

    def run(self):
        self.window.mainloop()


def test():
    print("Work was done")
    return 5

gui = Gui(test)

gui.run()