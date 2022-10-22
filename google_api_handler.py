from fileinput import close
import ezsheets

#handles all the dirty with google sheets but dont forget to download and set up credentials

def update_sheet(sheet_name,file_name):
    print("Updating spreadsheet...")
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
        print("Spreadsheet(" + sheet_name + ") updated with info from file:" + file_name)
