from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import requests
import threading
from time import sleep
from datetime import *

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


        self.startButton = ttk.Button(self.frm, text="Quit", command=lambda: self.validateRun(lambda: backFunction()))
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
        self.buttonPause = ttk.Button(newfrm, command=self.pause, text="STOP")
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
            self.buttonPause.configure(text="STOP")
            self.lock.release()
        else:
            self.buttonPause.configure(text="START")

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