from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import re
import difflib
from thread_parser import  *
from google_api_handler import update_sheet
import os

def remove_similar(file):
    #takes filename, removes repeat text entries from it
    with open(file, "r",encoding="utf-8") as f:
        item_list = []
        item_list = f.readlines()
        for i,j in enumerate(item_list):
            for y in range(i+1,len(item_list)):
                x = item_list[y]
                if(difflib.SequenceMatcher(lambda a: a in " ",j,x).ratio() > 0.8):
                    item_list.pop(y)
                    break
        with open(file, "w",1,"utf-8") as f:
            for item in item_list:
                f.write(item)
    #print(item_list)
    f.close()

def grab_time():
    #prompts for link, scrapes it and returns datetime obj
    almosttime = input("Input itsalmo.st link(part after the .st/ only): ")
    link = "https://itsalmo.st/" + almosttime
    while(is404(link)):
        almosttime = input("Invalid link, input again: ")
        link = "https://itsalmo.st/" + almosttime
    html = urlopen(link)
    bsobj = BeautifulSoup(html, 'html.parser')
    tag_contents = bsobj.find("script").string
    #str containing time, format = 2023-03-15T16:03:33.619000Z
    timestr = re.search("expires\":\"(.+)\"\,", tag_contents).group(1)
    datestamp = datetime.fromisoformat(timestr.replace("Z","")) #out without Z
    return datestamp
    
    

def main():

    thread_pattern = input("Insert thread pattern to look for: ")
    board = input("Insert board to scrape(letters only): ")
    spreadsheet = input("Insert the exact name of the google spreadsheet to use(if it does not already exist it will be created): ")
    sleep_minutes = 8 * 60
    minreplies = int(input("Insert the minimum number of replies needed for the post to be valid: "))
    endstamp = grab_time()

    file_name = "Nominations_list.txt"
    scraped = "scraped_threads.txt"

    while endstamp >= datetime.utcnow():
        if get_threadcatalog(thread_pattern, board):
            thread = get_threadcatalog(thread_pattern, board)
            while not(is404(thread) or isarchived(thread)):
                page = scrape_thread(thread,file_name,minreplies)
                if endstamp <= datetime.utcnow():
                    
                    xend = datetime.utcnow().strftime("%c")
                    print("Timer over, program closed at " + xend)
                    os.system("PAUSE")#windows specific but whatever
                    return #end program

                
                update_sheet(spreadsheet,file_name)
                remove_similar(file_name)
                print("Pausing program for " + str(sleep_minutes / page) + " seconds. ")
                print("-" * 30)
                sleep(sleep_minutes / page)#higher the page, the faster we scrape

        scrape_archived_thread(convert_to_archivepattern(thread_pattern),board,scraped,file_name, minreplies)

        remove_similar(file_name)
        update_sheet(spreadsheet,file_name)
        print("Pausing program for {sleep_minutes} minutes. ")
        print("-" * 30)
        sleep(sleep_minutes)


     #time over, end program
    xend = datetime.utcnow().strftime("%c")
    print("Timer over, program closed at " + xend)
    os.system("PAUSE")

if __name__ == "__main__":
    main()
    


   

