from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo

def newWindow(texts):
    showinfo("Input info", texts)

def makeEntry(lname, var, master, infoText):
    lPat = ttk.Label(master, text=lname)
    lPat.grid()
    tButton = ttk.Button(master, text="?", command= lambda: newWindow(infoText), width=1)
    Button.grid(self=tButton, column=1, row=lPat.grid_info()['row'])
    ttk.Entry(master, exportselection=0, textvariable=var).grid(padx=20, pady=5) #may want to alter later,
                                                                                 #perhaps could return this

root = Tk()
root.resizable(False, False)

frm = ttk.Frame(root, padding=10,)
frm.grid()
#user inputs to consume
threadPat = StringVar()
board = StringVar()
sheet = StringVar()
minReplies = StringVar()
endstamp = StringVar()

makeEntry("Thread pattern", threadPat, frm, 
"A word or sentence present in the thread OP to be searched, must be unique. ie: Nominations")

makeEntry("Board", board, frm, 
"Letter or word of the board to scrape. ie: v, a, trash")

makeEntry("Google Sheet", sheet, frm,
"Name of Google Sheets sheet to use, if inexistent it will be created. Uneeded if Google Sheets isn't set to be used.")

makeEntry("Minimum replies", minReplies, frm,
"Minimum replies for a nomination to be considered valid.")

makeEntry("itsalmo.st", endstamp, frm, 
"Link of the itsalmo.st timer to use. Part after the / only.")

ttk.Button(frm, text="Quit", command=root.destroy).grid(padx=20, pady=5)

root.mainloop()