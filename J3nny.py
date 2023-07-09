from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import re
import difflib
from thread_parser import  *
from google_api_handler import update_sheet, add_notice
import os

VERSION = "1.01" #for notice

diffratio = 0.8 #constant of similarity to use with difflib


def remove_invalids(file, blacklist):
    #takes filename, removes repeat text entries or blacklisted ones from it
    with open(file, "r",encoding="utf-8") as f:
        item_list = []
        item_list = f.readlines()
        for i,j in enumerate(item_list):
            #loop for removing repeated ones
            for y in range(i+1,len(item_list)):
                x = item_list[y]
                if(difflib.SequenceMatcher(lambda a: a in " ",j,x).ratio() > diffratio):
                    item_list.pop(y)
                    break
        if blacklist:
            for i in range(len(item_list)):
            #loop for removing blacklisted
                for x in blacklist:
                    if(difflib.SequenceMatcher(None,item_list[i], x).ratio() > diffratio):
                        item_list.pop(i)
                        break

        with open(file, "w",1,"utf-8") as f:
            for item in item_list:
                f.write(item)
    #print(item_list) #debug stuff

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
    
def clean_text(string):
    with open(string, "w",encoding="utf-8") as f:
        f.write('')
        f.close()

def get_blacklist():
    #return list of denied chars
    #or zero if user wants none
    try:
        open("blacklist.txt")
    except FileNotFoundError:
        print("blacklist.txt not found or empty! Proceeding without a blacklist.")
        return 0
    else:
        with open("blacklist.txt") as f:
            lst = f.readlines()
            if lst:
                return lst
            else:
                return 0

def insert_word(original: str, inp: str):
    #replaces original's middle with input if possible
    if len(original) >= len(inp):
        ohalf = int(len(original) / 2)
        ilen = int(len(inp))
        repl = ohalf - int(ilen /2)
        a = original[:repl]
        cut = int(repl + (ilen))
        b = original[cut:]
        newstrin = a + inp + b
        return newstrin
        

    return original

def enboxen(lst: list):
    #takes list of strings, changes it to be boxed
    #+-----+
    #|aaa  |
    #|bbbbb|
    #|ccc  |
    #+-----+
    #I just think it looks neat 
    #sheets doesnt have all characters the same lenght so looks weird there tho...
    #TODO: change it to look neat even with their character size dif

    max = 0
    for i in lst:
        if len(i) > max:
            max = len(i)
    if max > 3:


        for i in range(len(lst)):
            spacelen = max - len(lst[i])
            spaces = ' ' * spacelen 
            lst[i] = '|' + lst[i] + spaces + '|'
        
        top = '\'+' + ('-' * max) + '+' # needs the ' before so gogle sheets wont think its a formula
        lst.append(top)
        lst.insert(0, top)

        return lst
    return lst

def notice(lst: list):
    #builds and return notice, with or without blacklist
    if lst:
        newlst = lst
        max = 0
        for i in newlst:
            if len(i) > max:
                max = len(i)
        if max < len("https://github.com/ZamboLambo/J3nny"):
            max = len("https://github.com/ZamboLambo/J3nny")
        line = '-' * max
        newlst.insert(0, insert_word(line, "BlACKLIST"))
        newlst.insert(0, "https://github.com/ZamboLambo/J3nny")
        newlst.insert(0, "Source code:")
        enboxen(newlst)
        newlst[0] = insert_word(lst[0], "J3NNY v" + VERSION)
        return newlst
    newlst = ["Source code:", "https://github.com/ZamboLambo/J3nny"]
    enboxen(newlst)
    newlst[0] = insert_word(newlst[0], "J3NNY v" + VERSION)
    return newlst




def main():

    thread_pattern = input("Insert thread pattern to look for: ")
    board = input("Insert board to scrape(letters only): ")
    spreadsheet = input("Insert the name of the google spreadsheet to use(if it does not already exist it will be created): ")
    sleep_minutes = 8 * 60
    minreplies = int(input("Insert the minimum number of replies needed for the post to be valid: "))
    endstamp = grab_time()

    file_name = "Nominations_list.txt"
    scraped = "scraped_threads.txt"
    blacklst = get_blacklist()
    clean_text(file_name)
    note = notice(blacklst)

    add_notice(note, spreadsheet)


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
                remove_invalids(file_name)
                print(f"Pausing program for {sleep_minutes / page} seconds. ")
                print("-" * 30)
                sleep(sleep_minutes / page)#higher the page, the faster we scrape

        scrape_archived_thread(convert_to_archivepattern(thread_pattern),board,scraped,file_name, minreplies)

        remove_invalids(file_name, blacklst)
        update_sheet(spreadsheet,file_name)
        print(f"Pausing program for {sleep_minutes / 60} minutes. ")
        print("-" * 30)
        sleep(sleep_minutes)


     #time over, end program
    xend = datetime.utcnow().strftime("%c")
    print("Timer over, program closed at " + xend)
    os.system("PAUSE")

if __name__ == "__main__":
    main()
    

   

