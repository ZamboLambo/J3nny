import re
import difflib
import requests
from bs4 import BeautifulSoup
import pandas as pd
import glob
from threadClass import chanThread
from ast import literal_eval
import numpy as np
import os

import time

from google_api_handler import updateSheet, readSheet

def log(text):
    with open("log_file.txt", "a") as f:
        f.write(text + '\n')

def getThreadArchived(pattern,board): 
    #Gets first thread link from archive based on pattern
    #Pattern is thread title or if theres none, body of text
    #4chan archives automatically remove special characters, make it lowercase and replace spaces with -
    #return value is string or 0 if failed to find
    html = requests.get("https://boards.4chan.org/" + board + "/archive").text
    bsobj = BeautifulSoup(html, 'html.parser')
    match = str(bsobj.find(href = re.compile(pattern)))
    cut1 = re.split(pattern,match)
    cut2 = re.split("href=\"",cut1[0])
    if len(cut2) > 1:
        thread = "https://boards.4chan.org" + cut2[1]
        return thread
    return 0

def getThreadcatalog(pattern,board):
    #goes through catalog, returns thread link or 0 if failed to find
    html = requests.get("https://boards.4chan.org/" + board + "/catalog").text
    bsobj = BeautifulSoup(html, 'html.parser')
    script = bsobj.find_all("script")
    t = str(script[5])
    results = (re.search("(var catalog = {\"threads\":)(.*)(}})",t).group(2))
    old = results
    results = results.split(pattern)[0]
    if old == results:
        #pattern not found
        return 0
    matches = re.findall("\"(\d+)\"", results)
    matches.reverse()
    thread = "https://boards.4chan.org/" + board + "/thread/" + matches[1]
    return thread

def is_similar(a: str,b: str):
    diffratui = 0.7
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

def findNomination(post): 
    #tries to find a way to convert message to "character (series)"

    post = post.strip() #remove trailing spaces
    nomination = re.search("(Nominating|nominating|NOMINATING|nominate).*(from|FROM).*((\s\s$|[/.!?])|.$)",post)
    
    if nomination:
        x = re.sub("(Nominating|nominating|NOMINATING|nominate)",'', nomination.group())
        x = re.sub("[/.!?]",'',x,1)
        x = re.sub("(from |FROM )",'(',x)
        if re.match("\s{2,}", x):
            y = x.split("  ")
            x = y[0]
        x = x + ')'
        return x
    from_ = re.search("(from|FROM)",post)
    if from_:
        x = re.sub("(from |FROM )",'(' ,post)
        if re.match("\s{2,}", x):
            y = x.split("  ")
            x = y[0]
        x = x + ')'
        return x
    return post #no pattern, shove in as is

def remove_newlines(postmessage):
    newlines = re.findall("\n",postmessage)
    if(newlines):
        x = re.sub("\n", "  ", postmessage)
        return x
    return postmessage

def to_archivepattern(str):
    #converts given string to valid pattern in archive links
    str_ = str.lower()
    table = str_.maketrans('','',string.punctuation)
    str_ = str_.translate(table)
    table = str_.maketrans(' ', '-')
    str_ = str_.translate(table)
    return str_

def findLatest(tPattern, board):
    temp = getThreadcatalog(tPattern, board)
    if temp:
        return temp
    temp = getThreadArchived(tPattern, board)
    if temp:
        return temp
    else:
        return 0

def latestWithArchive(latest, archived):
    latest["id"] = latest["id"].astype(int)
    #join archive with latest, no repeats, all must be included
    merged = archived.merge(latest, on="id", how="outer")
    #merge with override of latest
    for i in merged.index:
        if merged.at[i, "youCount_x"] < merged.at[i, "youCount_y"] or (pd.isna(merged.at[i, "youCount_x"])):
            merged.at[i, "youCount_x"] = merged.at[i, "youCount_y"]
    merged.drop(columns=["youCount_y"], inplace=True)
    merged.rename(columns={"youCount_x" : "youCount"}, inplace=True)

    #merge without override using latest, only fill if archived is NaN
    #ie archive gets pushed over new
    dropIt = []
    for item in merged.columns:
        if item.endswith("_x"):
            part = item.partition("_")[0]
            dropIt.append(part + "_y")
            for i in merged.index:
                if isinstance(merged.at[i, item], list):
                    if pd.isna(merged.at[i, item]).size == 0:
                        merged.at[i, item] = merged.at[i, part + "_y"]
                else: 
                    if pd.isna(merged.at[i, item]):
                        merged.at[i, item] = merged.at[i, part + "_y"]
            merged.rename(columns={item : part}, inplace=True)
    merged.drop(columns=dropIt, inplace=True)
    merged["youCount"] = merged["youCount"].astype(int)
    return merged


def validate(row, minRep):
    #rowwise validation
    row["nomination"] = findNomination(row["text"])

    if row["status"].startswith("HOST_"):
        #host made decisions supersed all else
        return row
    else:
        #main validation proc
        if not row["hasFile"]:
            row["status"] = "NO_IMAGE_FILE"
            log(f"POST[{row.id}] SET OUT: NO FILE")
            return row
        if row["youCount"] < minRep:
            row["status"] = "BELOW_YOU_LIMIT"
            log(f"POST[{row.id}] SET OUT: TOO FEW YOUS")
            return row
        if len(row["nomination"]) > 120:
            row["status"] = "NOM_TOO_LONG"
            log(f"POST[{row.id}] SET OUT: NOMINATION TOO LONG")
            return row
        row["status"] = "ALLOWED"
        log(f"POST[{row.id}] SET IN: ALLOWED")
    return row

def scrapeSession(tPattern, board, sheet, minRep, connectGoogle):
    archiveExists = glob.glob('*.csv')

    log("===============SCRAPE START=======================")
    isNewThread = False
    start = time.time()
    if archiveExists:
        lastNumber = archiveExists[0].rstrip(".csv")
        tryLink = f"https://boards.4chan.org/{board}/thread/{lastNumber}"
        current = chanThread(link=tryLink)

        if not current.isAlive():

            isNewThread = True
            last = findLatest(tPattern, board)
            if not last:
                log("No new thread found")
                log("===============SCRAPE END=========================")
                return 10 #sleep 10 seconds
            log(f"Found thread: {last}")

            current = chanThread(link=last)
    else:
        last = findLatest(tPattern, board)
        if not last:
            log("No new thread found")
            log("===============SCRAPE END=========================")
            return 30 #sleep 30 seconds
        current = chanThread(link=last)
        log(f"Found thread: {last}")
    log("Scraped successfully")
    if "status" not in current.posts.columns:
        current.posts.insert(loc=5, column="status", value="")
    if "nomination" not in current.posts.columns:
        current.posts.insert(loc=6, column="nomination", value=pd.NA)
    
    print(f"It took: {time.time() - start}")
    currentLink = current.link
    current = current.posts.apply(validate, axis=1, args=(minRep,))


    if archiveExists:
        archive = pd.read_csv(archiveExists[0], converters={ "replies" : literal_eval, "youCount" : np.int64, "threadNumber" : np.int64}, encoding='utf-8', on_bad_lines='skip')

        log(f"READ: {archiveExists[0]} ")

        if isNewThread:
            lastNu = archive["threadNumber"].iat[-1]

            current.insert(loc=7, column="threadNumber", value=lastNu+1)
        else:
            lastNu = archive["threadNumber"].iat[-1]
            current.insert(loc=7, column="threadNumber", value=lastNu)

        archive.hasFile = archive.hasFile.replace({"True": True, "False": False})
        final = chanThread(dataFrame=latestWithArchive(current, archive))
        os.unlink(os.path.join(os.getcwd(),f'{archiveExists[0]}'))
    else:
        final = chanThread(dataFrame=current)
        if "threadNumber" not in final.posts.columns:
            final.posts.insert(loc=7, column="threadNumber", value=0)

    threadNumber = currentLink.split('/')
    threadNumber.reverse()
    threadNumber = threadNumber[0]

    final.posts.to_csv(f"{threadNumber}.csv", index=False,encoding='utf-8', float_format='%.0f') #save it in full
    log(f"WROTE: {threadNumber}.csv")

    nominationList = []
    grouped = final.posts.groupby("threadNumber")
    
    for i in range(grouped.ngroups):
        if((grouped.get_group(i)["nomination"]).any()):
            nominationList.append(f"Thread {i}")
        df = grouped.get_group(i)
        for index, row in df.iterrows():
            if not(row["status"].find("ALLOW") == -1):
                nominationList.append(row["nomination"])
    nominationList = [x for x in nominationList if str(x) != 'nan']
    ############## Final step, comunicate with sheets(if on), compare with current nom list, handle deviations
    if connectGoogle:
        response = readSheet(sheetName=sheet)
    else:
        try:
            with open("NOMINATIONS.txt", "r") as file:
                response = file.readlines()
        except OSError:
            response = []
    if response:
        for i in range(len(response)):
            response[i] = response[i].rstrip()
            
        log("GOT RESPONSE")
        listOfListsResponse = []
        for index, item in enumerate(response):
            temp = []
            if re.fullmatch("Thread \d{1,2}", item): #don't think we're ever getting >99 threads but just change this if needed
                for i in response[index+1:]:
                    if re.fullmatch("Thread \d{1,2}",i):
                        break
                    else:
                        temp.append(i)
            if len(temp):
                listOfListsResponse.append(temp)
        #same process for internal list, assuming no outside editing
        #they should be nigh identical, only internal's last thread list being longer
        listOfListsinter = []
        for index,item in enumerate(nominationList):
            temp = []
            if re.fullmatch("Thread \d{1,2}", item): 
                for i in nominationList[index+1:]:
                    if re.fullmatch("Thread \d{1,2}",i):
                        break
                    else:
                        temp.append(i)
            if len(temp):
                listOfListsinter.append(temp)

        for i in range(len(listOfListsResponse)-1): 
        #safe to assume both have the same amount of threads
        #TODO: the last added threads must be compared diferently
        #thus minus 1
            intern_ = sorted(listOfListsinter[i])
            outside = sorted(listOfListsResponse[i])

            if outside != intern_:
                if len(outside) > len(intern_):
                    #outside bigger than internal
                    #something got add, 
                    diference = len(outside) - len(intern_)
                    sliced = outside[diference:]
                    #add to intern
                    for item in sliced:
                        listOfListsinter[i].append(item)
                    #change csv where item is to
                    #have status HOST_ALLOWED
                    temp = pd.read_csv(f"{threadNumber}.csv")
                    for item in sliced:
                        temp.loc[temp["nomination"] == item, "status"] = "HOST_ALLOWED"
                    temp.to_csv(f"{threadNumber}.csv",mode="w+", float_format='%.0f')

                elif len(outside) < len(intern_):
                    #outside smaller than internal
                    #something got denied,
                    diference = len(intern_) - len(outside)
                    sliced = outside[diference:]
                    #remove from internautismi miku painos
                    listOfListsinter[i] = intern_[:diference] 
                    #change csv where item is to 
                    #have status HOST_DENIED
                    temp = pd.read_csv(f"{threadNumber}.csv")
                    for item in sliced:
                        temp.loc[temp["nomination"] == item, "status"] = "HOST_DENIED"
                    temp.to_csv(f"{threadNumber}.csv",mode="w+",float_format='%.0f')
                else:
                    #something got edited
                    #edit in internal too
                    edited = []
                    original = []
                    for i in range(len(outside)):
                        if outside[i] != intern_[i]:
                            original.append(intern_[i])
                            edited.append(outside[i])
                            intern_[i] = outside[i]

                    listOfListsinter[i] = intern_
                    #change csv nomination to this
                    temp = pd.read_csv(f"{threadNumber}.csv")
                    for i in range(len(original)):
                        temp.loc[temp["nomination"] == original[i], "nomination"] = edited[i]
                    temp.to_csv(f"{threadNumber}.csv",mode="w+", float_format='%.0f')
        nominationList = []
        for i in range(len(listOfListsinter)):
            if len(listOfListsinter[i]):
                nominationList.append(f"->Thread {i}")
            for it in listOfListsinter[i]:
                nominationList.append(it)
    #at last, after all the checking
    #write to file/sheet
    if connectGoogle:
        updateSheet(nominationList)
    else:
        try:
            with open("NOMINATIONS.txt", 'w') as f:
                f.write("\n".join(map(str, nominationList)))
        except OSError:
            with open("NOMINATIONS.txt", 'x') as f:
                f.write("\n".join(map(str, nominationList)))
    log("===============SCRAPE END=========================")
    return 30 #sleep 30 secs

start = time.time()
scrapeSession("Workweek edish", "int", None, 2, False)
end = time.time()
print(f"Full function took: {end - start}")
os.remove("NOMINATIONS.txt")
os.remove("log_file.txt")
os.remove(glob.glob("*.csv")[0])