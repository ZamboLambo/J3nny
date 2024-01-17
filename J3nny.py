from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import re
import difflib
from thread_parser import  *
from google_api_handler import update_sheet
import os

VERSION = "1.02" #for notice

diffratio = 0.7 #constant of similarity to use with difflib


def is_similar(a: str,b: str):
    if (re.search("\(.*\)", a) and re.search("\(.*\)", b)):
        #abides to character(series)
        series_a = re.findall("\(.*\)", a)[0]
        series_a = series_a[1:-1]

        series_b = re.findall("\(.*\)", b)[0]
        series_b = series_b[1:-1]

        if not(difflib.SequenceMatcher(a= series_a, b= series_b).ratio() > diffratio):
            return False #diferent series, not same char
        char_a = a.split('(', maxsplit=1)[0]
        char_b = b.split('(', maxsplit=1)[0]
        if (difflib.SequenceMatcher(a= char_a, b= char_b).ratio() > diffratio):
            names_a = char_a.split()
            names_b = char_b.split()
            if(len(names_a) == len(names_b)):
                for i in range(len(names_a)):
                    if not(difflib.SequenceMatcher(a= names_a[i], b= names_b[i]).ratio() > diffratio):
                        return False
                return True          
        else:
            return False
    else:
        return difflib.SequenceMatcher(a= a, b= b).ratio() > diffratio


def remove_invalids(file, blacklist):
    #takes filename, removes repeat text entries or blacklisted ones from it
    with open(file, "r",encoding="utf-8") as f:
        item_list = []
        item_list = f.readlines()
        for i in range(len(item_list)):
            #loop for removing repeated ones
            for y in range(i+1,len(item_list)):
                if(is_similar(item_list[i], item_list[y])):
                    item_list.pop(y)
                    break
        if blacklist:
            for i in range(len(item_list)):
            #loop for removing blacklisted
                for x in blacklist:
                    if(is_similar(a= x, b= item_list[i])):
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
        print("blacklist.txt not found! Proceeding without a blacklist.")
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

def log_date(filename):
    with open(filename, 'w') as f:
        date = datetime.today().isoformat()
        f.write(date)

def read_log(filename):
    try: 
        with open(filename, "r") as f:
            date = f.readline()
            #date = date.replace('(', '').replace(")", '').replace(',', '').replace(' ', '')
            return datetime.fromisoformat(date)
    except IOError:
        return False

def pause_timer(secs: int):
    #pauses program and shows a timer while function active

    if secs > 59:
        min = int(secs / 60)
        sec = secs - (int(secs / 60) * 60)
    else:
        min = 0
        sec = secs

    print(f"Pausing program for {min} minutes and {sec} seconds.")

    while min or sec:
        sys.stdout.write("\r")
        sys.stdout.write("Remaining pause time: {:02d}:{:02d}".format(min, sec)) 
        sys.stdout.flush()
        time.sleep(1)
        sec = sec - 1
        if sec < 1:
            min = min - 1
            sec = 59
            
            if min < 0:
                min = 0
                sec = 0
            if not(min == 0 and sec == 0):
                sys.stdout.write("\r")
                sys.stdout.write("Remaining pause time: {:02d}:00".format(min + 1)) 
                sys.stdout.flush()
            else:
                sys.stdout.write("\r")
                sys.stdout.write("Remaining pause time: 00:00") 
                sys.stdout.flush()
            time.sleep(1)

    sys.stdout.write("\r")
    print("Timer over.                              ")




def main():

    thread_pattern = input("Insert thread pattern to look for(Case sensitive): ")
    board = input("Insert board to scrape(letters only): ")
    spreadsheet = input("Insert the name of the google spreadsheet to use(if it does not already exist it will be created): ")
    sleep_minutes = 8 * 60
    minreplies = int(input("Insert the minimum number of replies needed for the post to be valid: "))
    endstamp = grab_time()

    #TODO: clean the gspread config before anything holy fuck I hate this

    file_name = "Nominations_list.txt"
    scraped = "scraped_threads.txt"
    datelog = "datelog.txt" #last day nominations was written to, to decide whether to clean it or not
    blacklst = get_blacklist()
    logged = read_log(datelog)

    if logged:
        if not(logged.isocalendar()[1] == datetime.today().isocalendar()[1] \
            and logged.year == datetime.today().year):
            #dates arent within the same week
            #assuming: no tourneys in same week
            #ergo diferent tourney from before, clean noms
            clean_text(file_name)



    note = notice(blacklst)


    while endstamp >= datetime.utcnow():
        if get_threadcatalog(thread_pattern, board):
            thread = get_threadcatalog(thread_pattern, board)
            while not(is404(thread) or isarchived(thread)):
                if endstamp <= datetime.utcnow():
                    
                    xend = datetime.utcnow().strftime("%c")
                    print("Timer over, program closed at " + xend)
                    os.system("PAUSE")#windows specific but whatever
                    return #end program

                page = scrape_thread(thread,file_name,minreplies)
                remove_invalids(file_name, blacklst)
                update_sheet(spreadsheet,file_name, note)
                log_date("datelog.txt")
                pause_timer(int(sleep_minutes / page))#higher the page, the faster we scrape
                print("-" * 30)

        scrape_archived_thread(convert_to_archivepattern(thread_pattern),board,scraped,file_name, minreplies)

        remove_invalids(file_name, blacklst)
        update_sheet(spreadsheet,file_name, note)
        log_date("datelog.txt")
        pause_timer(int(sleep_minutes))
        print("-" * 30)


     #time over, end program
    xend = datetime.utcnow().strftime("%c")
    print("Timer over, program closed at " + xend)
    os.system("PAUSE")

if __name__ == "__main__":
    main()
    

   

