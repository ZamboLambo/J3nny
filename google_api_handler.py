from fileinput import close
import ezsheets
import os

#handles all the dirty with google sheets


def update_sheet(sheet_name,file_name, notice):
    print("Updating spreadsheet...")

    try: ezsheets.init()

    except ezsheets.EZSheetsException():
        #common exception outdated pickles
        #delete the old ones and try again
        if os.path.exists("token-drive.pickle"):
            os.remove("token-drive.pickle")
            os.remove("token-sheets.pickle")
        else:
            #init failed but no pickles found, user probs forgot
            #the credentials
            #nothing to do but warn then halt
            print("Unable to iniate sheet API. Did you remember to set up credentials?")
            os.system("PAUSE")
    finally: ezsheets.init()


    try: ss = ezsheets.Spreadsheet(sheet_name)

    except ezsheets.EZSheetsException: ss = ezsheets.createSpreadsheet(sheet_name)

    finally: 
        list_ = []
        with open(file_name,'r', encoding = 'utf-8') as f:
            for item in f:
                list_.append(item)
        f.close()
        ss.sheets[0].clear()
        ss.sheets[0].updateColumn(1,list_)
        add_notice(notice, sheet_name)
        print("Spreadsheet(" + sheet_name + ") updated with info from file: " + file_name)

def add_notice(notice, sheet_name):
    #put notice on collumn 2

    ss = ezsheets.Spreadsheet(sheet_name)
    ss.sheets[0].updateColumn(2,notice) 
