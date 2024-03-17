from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import requests
import threading
from time import sleep
from datetime import *

from random import randint

from os import mkdir
from sys import exit

from images import *

from scraper import log

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


        self.startStopButton = ttk.Button(self.frm, image=self.startIco, command=lambda: self.validateRun(backFunction))
        self.startStopButton.grid(padx=20, pady=5)

    def lockEntry(self):
        #for some reason all but almo got returned as a lenght 1 tuple...
        self.almo["state"] = 'disabled'
        self.minRep[0]["state"] = 'disabled'
        self.sheet[0]["state"] = 'disabled'
        self.board[0]["state"] = 'disabled'
        self.threadPat[0]["state"] = 'disabled'
        
    def mkhisdir(selh):
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

        self.thread = threading.Thread(target=lambda: self.doWork(func), daemon=True)
        self.thread.start()
        

    def resetUI(self, backFunc):
        self.almo["state"] = 'normal'
        self.minRep[0]["state"] = 'normal'
        self.sheet[0]["state"] = 'normal'
        self.board[0]["state"] = 'normal'
        self.threadPat[0]["state"] = 'normal'
        self.startStopButton.configure(command=lambda: self.validateRun(backFunc))
        self.startStopButton.configure(image=self.startIco)
        self.stateInfo.destroy()

    def updateState(self):
        while datetime.now() < self.end:
            left = self.end - datetime.now()
            try: 
                self.stateInfo.configure(text=str(left).rpartition('.')[0])
            except TclError:
                exit()
            sleep(1) # no need to update every microsecond if we're ignoring those
        self.stateInfo.configure(text="OVER", foreground="red")

    def doWork(self, func):

        timerThread = threading.Thread(target=self.updateState, daemon=True)
        timerThread.start()
        
        x = func()
        while datetime.now() < self.end:
            try:
                self.pauseTimer(x)
                x = func()
            except Exception as e:               
                log("SCRAPE ERROR: " + repr(e))
                log("LAST ERROR MESSAGE: " + str(e))
                showerror("ERROR", "During bot execution an unexpected error has happened. Error message saved on log_file. Current run terminated.")
                self.resetUI(func)
                exit()
                


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
    x = randint(0, 110)
    if x < 25:
        raise RuntimeError
    return 5

gui = Gui(test)

gui.run()


