from pyexpat import features
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import re
import difflib
from thread_parser import *

thread_pattern = "mr-co"
board = "co"
sleep_minutes = 5
minreplies = 8

#Gets first thread link from archive based on pattern
#Pattern is thread title or if theres none, body of text
#4chan archives automatically remove special characters, make it lowercase and replace spaces with -
#return value is string
def get_thread(pattern,board): 
    html = urlopen("https://boards.4channel.org/" + board + "/archive")
    bsobj = BeautifulSoup(html, 'html.parser')
    match = str(bsobj.find(href = re.compile(pattern)))
    cut1 = re.split(pattern,match)
    cut2 = re.split("href=\"",cut1[0])
    thread = "https://boards.4channel.org" + cut2[1]
    return thread

#takes filename, removes repeat text entries from it
def remove_similar(file):
    with open(file, "r") as f:
        item_list = []
        item_list = f.readlines()
        for i,j in enumerate(item_list):
            for y in range(i+1,len(item_list)):
                x = item_list[y]
                if(difflib.SequenceMatcher(lambda a: a in " ",j,x).ratio() > 0.65):
                    item_list.pop(y)
                    break
        with open(file, "w") as f:
            for item in item_list:
                f.write(item)
    print(item_list)
    f.close()

def main():
    file_name = "Nominations_list.txt"
    while(True):
        
        try:
            open("scraped_threads.txt")
        except FileNotFoundError:
            open("scraped_threads.txt",'x')
        finally:
            threads_list = []
            f = open("scraped_threads.txt","r+")
            fields = []
            for line in f:
                fields = line.split()

            curr_thread = get_thread(thread_pattern,board)

            if curr_thread not in fields: 
                print("Beginning scrape routine of " + curr_thread)
                f.write(curr_thread + "\n") #unscraped thread, append to list and scrape
                f.close()
                post_list = get_posts(curr_thread)
                character_list = handle_posts(post_list,minreplies)
                

                try:
                    open(file_name)
                except FileNotFoundError:
                    open(file_name,'x')
                finally:
                    a = open(file_name,"a")
                    for item in character_list:
                        a.write(item + "\n")
                    a.close()

                    print(str(len(character_list)) + " nominations added to nomination file.")


            else:
                f.close() #scraped already, close file and do nothing



        remove_similar(file_name)
        print("Going off for " + str(sleep_minutes) + " minutes")
        sleep(sleep_minutes * 60)


    return 0

if __name__ == "__main__":
    main()



