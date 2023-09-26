from fileinput import close
import gspread
import os
import glob

#handles all the dirty with google sheets


def update_sheet(sheet_name, file_name, notice):
    print("Updating spreadsheet...")
    dir_path = os.path.dirname(os.path.realpath(__file__))

    os.chdir(dir_path)
    credentials = glob.glob("*.json")
    
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0])
    
    try: client.open(sheet_name)

    except gspread.SpreadsheetNotFound:
        client.create(sheet_name)
    finally:
        sheet = client.open(sheet_name).sheet1
        list = []
        with open(file_name, 'r', encoding= 'utf-8') as f:
            for item in f:
                list.append(item)

        lists = []
        for i in list:
            l = [i]
            lists.append(l)
        #character list done, add notice

        for i in range(len(notice)):
            lists[i].append(notice[i])


        sheet.clear()
        sheet.update('A1', lists)
