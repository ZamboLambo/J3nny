from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re
import difflib
from thread_parser import  handle_posts, convert_to_pattern
from google_api_handler import update_sheet

thread_pattern = convert_to_pattern(input("Insert thread pattern to look for: "))
board = input("Insert board to scrape(letters only): ")
spreadsheet = input("Insert the exact name of the google spreadsheet to use(if it does not already exist it will be created): ")
sleep_minutes = 10
minreplies = int(input("Insert the minimum number of replies needed for the post to be valid: "))

#Gets first thread link from archive based on pattern
#Pattern is thread title or if theres none, body of text
#4chan archives automatically remove special characters, make it lowercase and replace spaces with -
#return value is string or 0 if failed to find
def get_thread(pattern,board): 
    html = urlopen("https://boards.4channel.org/" + board + "/archive")
    bsobj = BeautifulSoup(html, 'html.parser')
    match = str(bsobj.find(href = re.compile(pattern)))
    cut1 = re.split(pattern,match)
    cut2 = re.split("href=\"",cut1[0])
    if len(cut2) > 1:
        thread = "https://boards.4channel.org" + cut2[1]
        return thread
    return 0

#takes filename, removes repeat text entries from it
def remove_similar(file):
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
    f.close()

def main():
    file_name = "Nominations_list.txt"
    scraped = "scraped_threads.txt"
    while(True):
        
        try:
            open(scraped)
        except FileNotFoundError:
            open(scraped,'x')
        finally:
            f = open(scraped,"r+", encoding="utf-8")
            fields = []
            for line in f:
                fields = line.split()

            curr_thread = get_thread(thread_pattern,board)

            if curr_thread and curr_thread not in fields: 
                print("Beginning scrape routine of " + curr_thread)
                f.write(curr_thread + "\n") #unscraped thread, append to list and scrape
                f.close()

                options = webdriver.FirefoxOptions()
                options.add_argument("--headless")

                driver = webdriver.Firefox(options=options)
                driver.get(curr_thread)
                sleep(5)
                post_list = driver.find_elements(By.CLASS_NAME, 'postContainer')
                character_list = handle_posts(post_list,minreplies)
                
                driver.close()
                try:
                    open(file_name)
                except FileNotFoundError:
                    open(file_name,'x')
                finally:
                    a = open(file_name,"a", encoding="utf-8")
                    for item in character_list:
                        if (item != "" and item != " " and len(item) < 100):
                            a.write(item + "\n")
                    a.close()

                    print(str(len(character_list)) + " nominations added to nomination file.")


            else:
                f.close() #scraped already, close file and do nothing



        remove_similar(file_name)
        update_sheet(spreadsheet,file_name)
        print("Going to sleep for " + str(sleep_minutes) + " minutes")
        print("-" * 30)
        sleep(sleep_minutes * 60)


    return 0

if __name__ == "__main__":
    main()

