from fileinput import close
import gspread
import os
import glob
from time import sleep

#handles all the dirty with google sheets
def log(text):
    with open("log_file.txt", "a") as f:
        f.write(text + '\n')

def updateSheet(sheetName, list_):
    #turn list into list of lists because gspread demands that format
    list_ = [[x] for x in list_]


    log("Updating spreadsheet...")
    dir_path = os.getcwd()
    credentials = glob.glob("*.json")
    credentials.reverse()
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0],
                            authorized_user_filename= dir_path + "/authorized_user.json")
    
    try: client.open(sheetName)

    except gspread.SpreadsheetNotFound: 
        client.create(sheetName)
    except gspread.exceptions.APIError:
        log("API ERROR ON UPDATE, WAITING 30 SECONDS AND RE-TRYING")
        sleep(30)
        updateSheet(sheetName, list_)
        return
    finally:
        log("Opening sheet")
        sheet = client.open(sheetName).sheet1
        sheet.batch_clear(['A:A'])
        sheet.update(list_)
        log("Updated.")

def isSheetEmpty(sheetName):
    dir_path = os.getcwd()
    credentials = glob.glob("*.json")
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0],
                            authorized_user_filename= dir_path + "/authorized_user.json")
    try:
        sheet = client.open(sheetName).sheet1
    except gspread.SpreadsheetNotFound:
        return True
    sheet = sheet.col_values(1)
    for i in sheet:
        if i != None:
            return False
    return len(sheet) > 0
def eraseFirstCol(sheetName):
    dir_path = os.getcwd()
    credentials = glob.glob("*.json")
    credentials.reverse()
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0],
                            authorized_user_filename= dir_path + "/authorized_user.json")
    sheet = client.open(sheetName).sheet1
    sheet.batch_clear(['A:A'])

def readSheet(sheetName):
    dir_path = os.getcwd()
    credentials = glob.glob("*.json")
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0],
                            authorized_user_filename= dir_path + "/authorized_user.json")
    try:
        sheet = client.open(sheetName).sheet1
    except gspread.SpreadsheetNotFound:
        return []
    except gspread.exceptions.APIError:
        log("API ERROR ON READ, WAITING 30 SECONDS AND RE-TRYING")
        sleep(30)
        return readSheet(sheetName)
    sheet = sheet.col_values(1)
    return sheet