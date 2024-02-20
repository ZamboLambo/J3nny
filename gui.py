from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import requests

def newWindow(texts):
    showinfo("Input info", texts)

def makeEntry(lname, var, master, infoText):
    lPat = ttk.Label(master, text=lname)
    lPat.grid()
    tButton = ttk.Button(master, text="?", command= lambda: newWindow(infoText), width=1)
    Button.grid(self=tButton, column=1, row=lPat.grid_info()['row'])
    tEntry = ttk.Entry(master, exportselection=0, textvariable=var)
    tEntry.grid(padx=20, pady=5)
    return tEntry


class gui:
    #user inputs to consume
    def __init__(self, frm):
        self.threadPat = StringVar()
        self.board = StringVar()
        self.sheet = StringVar()
        self.minReplies = StringVar()
        self.endstamp = StringVar()
        self.tPat = makeEntry("Thread pattern", self.threadPat, frm, 
"A word or sentence present in the thread OP to be searched, must be unique. ie: Nominations"),

        self.board = makeEntry("Board", self.board, frm, 
        "Letter or word of the board to scrape. ie: v, a, trash"),

        self.gSheet = makeEntry("Google Sheet", self.sheet, frm,
        "Name of Google Sheets sheet to use, if inexistent it will be created. Uneeded if Google Sheets isn't set to be used."),

        self.minRep = makeEntry("Minimum replies", self.minReplies, frm,
        "Minimum replies for a nomination to be considered valid."),

        self.almo = makeEntry("itsalmo.st", self.endstamp, frm, 
        "Link of the itsalmo.st timer to use. Part after the / only.")


        ttk.Button(frm, text="Quit", command=lambda: self.validate()).grid(padx=20, pady=5)
    def validate(self):
        showerror(self.threadPat.get(), self.threadPat.get())




root = Tk()
root.resizable(False, False)

frm = ttk.Frame(root, padding=10,)
frm.grid()


gui = gui(root)



root.mainloop()