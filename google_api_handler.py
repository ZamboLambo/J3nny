from fileinput import close
import gspread
import os
import glob
from scraper import log
from time import sleep

#handles all the dirty with google sheets


def updateSheet(sheetName, list_):
    #turn list into list of lists because gspread demands that format
    list_ = [[x] for x in list_]


    log("Updating spreadsheet...")
    dir_path = os.getcwd()
    credentials = glob.glob("*.json")
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0],
                            authorized_user_filename= dir_path + "/authorized_user.json")
    
    try: client.open(sheetName)

    except gspread.SpreadsheetNotFound:
        client.create(sheetName)
    finally:
        sheet = client.open(sheetName).sheet1
        sheet.update(list_)
        sleep(0.250)

#sleeping is just for safeness case to not extrapolate how much google allows to call the API
def readSheet(sheetName):
    dir_path = os.getcwd()
    credentials = glob.glob("*.json")
    client = gspread.oauth(credentials_filename= dir_path + '/' + credentials[0],
                            authorized_user_filename= dir_path + "/authorized_user.json")
    sheet = client.open(sheetName).sheet1
    sleep(0.250)
    return sheet.col_values(1)

print(readSheet("test"))