from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import requests
import threading
from time import sleep

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
"Name of Google Sheets sheet to use, if inexistent it will be created. Uneeded if Google Sheets isn't set to be used."),

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

        self.stateInfo = ttk.Label(newfrm, text="I AM ERROR", background="black",
         foreground="green2", padding=10)
        self.stateInfo.grid()

        thread = threading.Thread(target=lambda: self.doWork(func), daemon=True)
        thread.start()
        #if paused is on and tkinter is closed via the top right x button the thread will live on


    def doWork(self, func):
        x = func()
        while x > 0:
            self.pauseTimer(x)
            x = func()


    def pause(self):
        if self.paused.get():
            self.buttonPause.configure(text="STOP")
        else:
            self.buttonPause.configure(text="START")

        self.paused.set(not(self.paused.get()))

    def pauseTimer(self, secs):      
            if secs > 59:
                min = int(secs / 60)
                sec = secs - (int(secs / 60) * 60)
            else:
                min = 0
                sec = secs
            self.stateInfo.configure(text= "{:02d}:{:02d}".format(min, sec))

            while min or sec:

                if self.paused.get():
                    self.window.wait_variable(self.paused)
                self.stateInfo.configure(text= "{:02d}:{:02d}".format(min, sec))
                sleep(1)
                sec = sec - 1
                if sec < 1:
                    min = min - 1
                    sec = 59
                    
                    if min < 0:
                        min = 0
                        sec = 0
                    if not(min == 0 and sec == 0):
                        self.stateInfo.configure(text= "{:02d}:{:02d}".format(min, sec))
                    else:
                        self.stateInfo.configure(text= "00:00")
                    sleep(1)

    def run(self):
        self.window.mainloop()


def test():
    return 5

gui = Gui(test)

gui.run()