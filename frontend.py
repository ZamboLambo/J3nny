from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import requests
import threading
from time import sleep
from datetime import *


from os import mkdir

from images import *

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

        self.startIco = startIcon()
        self.stopIco = pauseIcon()
        


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


        self.startStopButton = ttk.Button(self.frm, image=self.startIco, command=lambda: self.validateRun(lambda: backFunction()))
        self.startStopButton.grid(padx=20, pady=5)


    def lockEntry():
        #for some reason all but almo got returned as a lenght 1 tuple...
        self.almo["state"] = 'disabled'
        self.minRep[0]["state"] = 'disabled'
        self.sheet[0]["state"] = 'disabled'
        self.board[0]["state"] = 'disabled'
        self.threadPat[0]["state"] = 'disabled'
    def mkhisdir():
        try:
            mkdir("DATA")
        except FileExistsError:
            pass


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

        self.lockEntry()

        self.mkhisdir()

        self.paused = BooleanVar(value=False)

        self.startStopButton.configure( command=self.pause, image=self.stopIco)

        self.end = datetime.now() + timedelta(hours=1)

        self.stateInfo = ttk.Label(self.frm, text="I AM ERROR", background="black",
         foreground="green2", padding=10, justify="center")
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
            self.startStopButton.configure(image=self.stopIco)
            self.lock.release()
        else:
            self.startStopButton.configure(image=self.startIco)

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


