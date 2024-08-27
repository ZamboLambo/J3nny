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
import lxml
import json
import ast

import time

from google_api_handler import updateSheet, readSheet

chanLink = "https://boards.4chan.org/"
logEnd = "===============SCRAPE END========================="

def log(text):
    with open("log_file.txt", "a") as f:
        f.write(text + '\n')

def getThreadArchived(pattern,board): 
    #Gets first thread link from archive based on pattern
    #Pattern is thread title or if theres none, body of text
    #4chan archives automatically remove special characters, make it lowercase and replace spaces with -
    #return value is string or 0 if failed to find
    html = requests.get(chanLink + board + "/archive").text
    bsobj = BeautifulSoup(html, 'lxml')
    match = str(bsobj.find(href = re.compile(pattern)))
    cut1 = re.split(pattern,match)
    cut2 = re.split("href=\"",cut1[0])
    if len(cut2) > 1:
        thread = "https://boards.4chan.org" + cut2[1]
        return thread
    return 0

def getThreadcatalog(pattern,board):
    #goes through catalog, returns thread link or 0 if failed to find
    html = requests.get(chanLink + board + "/catalog").text
    results = (re.search("(var catalog = {\"threads\":)(.*)(}})",html).group(2))
    old = results
    results = results.split(pattern)[0]
    if old == results:
        #pattern not found
        return 0
    matches = re.findall("\"(\d+)\"", results)
    matches.reverse()
    thread = chanLink + board + "/thread/" + matches[1]
    return thread

def is_similar(a: str,b: str):
    rePattern = "\(.*\)" #character(series) get series
    diffratio = 0.7
    if (re.search(rePattern, a) and re.search(rePattern, b)):
        #abides to character(series)
        series_a = re.findall(rePattern, a)[0]
        series_a = series_a[1:-1]

        series_b = re.findall(rePattern, b)[0]
        series_b = series_b[1:-1]

        if (difflib.SequenceMatcher(a= series_a, b= series_b).ratio() <= diffratio):
            return False #diferent series, not same char
        char_a = a.split('(', maxsplit=1)[0]
        char_b = b.split('(', maxsplit=1)[0]
        if (difflib.SequenceMatcher(a= char_a, b= char_b).ratio() > diffratio):
            return isSameName(char_a, char_b)         
        else:
            return False
    return difflib.SequenceMatcher(a= a, b= b).ratio() > diffratio

def isSameName(a, b):
    names_a = a.split()
    names_b = b.split()
    if(len(names_a) == len(names_b)):
        for i in range(len(names_a)):
            if (difflib.SequenceMatcher(a= names_a[i], b= names_b[i]).ratio() <= diffratio):
                return False
        return True 

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
        x = str.replace("\n", "  ", postmessage)
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
    findDups(merged, dropIt)
    merged.drop(columns=dropIt, inplace=True)
    merged["youCount"] = merged["youCount"].astype(int)
    return merged

def findDups(merged, dropIt):
    for item in merged.columns:
        if item.endswith("_x"):
            part = item.partition("_")[0]
            dropIt.append(part + "_y")
            for i in merged.index:
                renameIfList(merged, i, item, part)
            merged.rename(columns={item : part}, inplace=True)
            
def renameIfList(merged, i, item, part):
    if isinstance(merged.at[i, item], list):
        if pd.isna(merged.at[i, item]).size == 0:
            merged.at[i, item] = merged.at[i, part + "_y"]
    else: 
        if pd.isna(merged.at[i, item]):
            merged.at[i, item] = merged.at[i, part + "_y"]



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
            return row
        if row["youCount"] > minRep:
            row["status"] = "BELOW_YOU_LIMIT"
            return row
        if len(row["nomination"]) > 120:
            row["status"] = "NOM_TOO_LONG"
            return row
        row["status"] = "ALLOWED"
    return row

def scrapeSession(tPattern, board, sheet, minRep, connectGoogle):
    archiveExists = glob.glob('*.csv')

    log("===============SCRAPE START=======================")
    isNewThread, current, currentLink = tryFindThread(archiveExists, board, minRep, tPattern)
    if (current.empty):
        return 30

    nominationList, threadNum = handleThreadArchive(current, archiveExists, isNewThread, currentLink)

    nomFile = "NOMINATIONS.txt"
    
    ############## Final step, comunicate with sheets(if on), compare with current nom list, handle deviations
    response = connectOrReadOutsideFile(connectGoogle, nomFile)
    if response:
        listOfListsResponse, listOfListsinter = formatThread(response, [])
        
        for index in range(len(listOfListsResponse)):
            intern_ = sorted(listOfListsinter[index])
            outside = sorted(listOfListsResponse[index])

            handleDeviations(intern_, outside, listOfListsinter, threadNum, index)

            
        nominationList = []
        for i in range(len(listOfListsinter)):
            if len(listOfListsinter[i]):
                nominationList.append(f"->Thread {i}")
            for it in listOfListsinter[i]:
                nominationList.append(it)

    jsonList = json.dumps(nominationList)
    with open('A_expected.json', 'w') as f:
        json.dump(jsonList, f)
    #at last, after all the checking
    #write to file/sheet
    sendAndArchive(connectGoogle, sheet, nominationList, nomFile)
    log(logEnd)

    return returnTime(int(threadNum), board)

def handleDeviations(intern_, outside, listOfListsinter, threadNumber, index):
    if outside != intern_:
        if len(outside) > len(intern_):
            #outside bigger than internal
            #something got added
            sliced = [x for x in outside if x not in intern_]
            #add to intern
            for item in sliced:
                listOfListsinter.append(item)
            #change csv where item is to
            #have status HOST_ALLOWED
            temp = pd.read_csv(f"{threadNumber}.csv", sep=';')
            for item in sliced:
                chara = re.findall(".+(?=\()")[0]
                series = re.findall("(?<=\().+(?=\))")[0]
                #looks for the exact nomination given
                #ergo if it doesnt fit what the robot thinks
                #then the status is never truly changed
                temp.loc[temp["nomination"].str.match(f"(?<={chara}).*(?={series})"), "status"] = "HOST_ALLOWED"
            temp.to_csv(f"{threadNumber}.csv",mode="w+", float_format='%.0f', index=False, sep=';')

        elif len(outside) < len(intern_):

            
            #outside smaller than internal
            #something got denied,
            diference = len(intern_) - len(outside)
            sliced = [x for x in intern_ if x not in outside]
            #remove from internautismi miku painos
            listOfListsinter = intern_[:diference] 
            #change csv where item is to 
            #have status HOST_DENIED
            temp = pd.read_csv(f"{threadNumber}.csv", sep=';')
            for item in sliced:
                temp.loc[temp["nomination"] == item, "status"] = "HOST_DENIED"
            temp.to_csv(f"{threadNumber}.csv",mode="w+",float_format='%.0f', index=False, sep=';')
        else:
            overrideInternal(intern_, outside, listOfListsinter, index, threadNumber)
            
    return listOfListsinter

def returnTime(threadNumber: int, board):
    resp = requests.get(f'https://a.4cdn.org/{board}/threads.json')

    if(resp.status_code < 200 or resp.status_code > 399):
        return 15

    df = pd.json_normalize(resp.json())

    for i in df.iterrows():
        pars = (i[1]['threads'])
        for index, thread in enumerate(pars):
            if threadNumber == thread['no']:
                return calcSleepTime(i[1]['page'], len(pars), index)
    return 15

def calcSleepTime(page, pageLenght, pagePos):
    if(page <= 5):
        return 60 * 5 #page at or below five is safe, sleep five minutes
    if(page < 10):
        return 60 * (10 - page) #less so, sleep less
    #10 is danger zone for possible misses
    #specially with possible spam
    #cap at 5 secs at minimum tho
    x = 60 * ((pageLenght - pagePos) / pageLenght)
    if x > 5:
        return x
    return 5

def overrideInternal(intern_, outside, listOfListsinter, index, threadNumber):
    #something got edited
    #edit in internal too
    edited = []
    original = []
    for i in range(len(outside)):
        if outside[i] != intern_[i]:
            original.append(intern_[i])
            edited.append(outside[i])
            intern_[i] = outside[i]

    listOfListsinter[index] = intern_
    #change csv nomination to this
    temp = pd.read_csv(f"{threadNumber}.csv", sep=';')
    for i in range(len(original)):
        temp.loc[temp["nomination"] == original[i], "nomination"] = edited[i]
    temp.to_csv(f"{threadNumber}.csv",mode="w+", float_format='%.0f', index=False, sep=';')


def hasNominee(post, nominee):
    character = re.findall(".*(?=\()", nominee)[0]
    series = re.findall("(?<=\().*(?=\))", nominee)
    return re.match(f"(?={character}).*(?={series})", post) != None

def formatThread(response, listOfListsinter):
    threadRegex = "Thread \d{1,2}" #don't think we're ever getting >99 threads but just change this if needed

    for i in range(len(response)):
        response[i] = response[i].rstrip()
            
    log("GOT RESPONSE")
    listOfListsResponse = []
    for index, item in enumerate(response):
        temp = []
        if re.fullmatch(threadRegex, item): 
            for i in response[index+1:]:
                if re.fullmatch(threadRegex,i):
                    break
                else:
                    temp.append(i)
        if len(temp):
            listOfListsResponse.append(temp)
        #same process for internal list of last sent response, assuming no outside editing
        #they should be identical
    try:
        with open("A_expected.json","r") as f:
            lastResponse = json.loads(f.read())
            lastResponse = ast.literal_eval(lastResponse)
    except OSError:
        lastResponse = None
    
    lastResponseToInternalList(lastResponse, listOfListsinter, threadRegex)
    return listOfListsResponse, listOfListsinter

def lastResponseToInternalList(lastResponse, listOfListsinter, threadRegex):
    if not(lastResponse):
        return
    for index,item in enumerate(lastResponse):
        temp = []
        if re.fullmatch(threadRegex, item): 
            for i in lastResponse[index+1:]:
                if re.fullmatch(threadRegex,i):
                    break
                else:
                    temp.append(i)
        if len(temp):
            listOfListsinter.append(temp)    

def connectOrReadOutsideFile(connectGoogle, nomFile):
    if connectGoogle:
        response = readSheet(sheetName=sheet)
    else:
        try:
            with open(nomFile, "r") as file:
                response = file.readlines()
        except OSError:
            response = []
    return response

def handleThreadArchive(current, archiveExists, isNewThread, currentLink):
    if archiveExists:
        archive = pd.read_csv(archiveExists[0], converters={ "replies" : literal_eval, "youCount" : np.int64, "threadNumber" : np.int64}, encoding='utf-8', on_bad_lines='skip', sep=';')

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
    final.posts.to_csv(f"{threadNumber}.csv", index=False,encoding='utf-8', float_format='%.0f', sep=';') #save it in full
    log(f"WROTE: {threadNumber}.csv")

    nominationList = []
    grouped = final.posts.groupby("threadNumber")
    
    for i in range(grouped.ngroups):
        if((grouped.get_group(i)["nomination"]).any()):
            nominationList.append(f"Thread {i}")
        df = grouped.get_group(i)
        for index, row in df.iterrows():
            if (row["status"].find("ALLOW") != -1):
                nominationList.append(row["nomination"])
    return [x for x in nominationList if str(x) != 'nan'], threadNumber


def tryFindThread(archiveExists, board, minRep, tPattern):
    isNewThread = False
    if archiveExists:
        lastNumber = archiveExists[0].rstrip(".csv")
        tryLink = f"https://boards.4chan.org/{board}/thread/{lastNumber}"
        current = chanThread(link=tryLink)

        if not current.isAlive():

            isNewThread = True
            last = findLatest(tPattern, board)
            if not last:
                log("No new thread found")
                log(logEnd)
                return isNewThread, pd.Dataframe(), None
            log(f"Found thread: {last}")

            current = chanThread(link=last)
    else:
        last = findLatest(tPattern, board)
        if not last:
            log("No new thread found")
            log(logEnd)
            return isNewThread, pd.DataFrame(), None
        current = chanThread(link=last)
        log(f"Found thread: {last}")
    log("Scraped successfully")
    if "status" not in current.posts.columns:
        current.posts.insert(loc=5, column="status", value="")
    if "nomination" not in current.posts.columns:
        current.posts.insert(loc=6, column="nomination", value=pd.NA)
    
    currentLink = current.link
    current = current.posts.apply(validate, axis=1, args=(minRep,))##<-- typeError
    return isNewThread, current, currentLink

def sendAndArchive(connectGoogle, sheet, nominationList, nomFile):
    if connectGoogle:
        updateSheet(sheet, nominationList)
    else:
        try:
            with open(nomFile, 'w') as f:
                f.write("\n".join(map(str, nominationList)))
        except OSError:
            with open(nomFile, 'x') as f:
                f.write("\n".join(map(str, nominationList)))