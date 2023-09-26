# Archive-Nombot
A Python script to automate parts of the job of tourney hosts on 4channel. 

# Setting up

1 -Download the current release "j3nny.7z" and unzip it. (Standalone built with Pyinstaller, Windows only. Works with win7 and later.)

2 -Download the google api credentials. (see: https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id -> get the Oauth)

3 -Place those files inside the folder where "j3nny.exe" is.

4 -Make sure you have Mozilla Firefox. 

5 -Make sure you are logged into your google account.

6 -(Optional) Create a "blacklist.txt" file, with one of the denied characters per line. Format: character(media it's from)

7 -Launch "j3nny.exe"

# About the bot

 Inputs needed: thread pattern to look for(a unique word or words in the title will suffice), board, name of google spreadsheet, minimum replies and link of almo.st timer, optionally a blacklist text file.
 
 Runs until the current time is above the given timer or process is stopped.
 
 Updates the given spreadsheet with info scraped.

# Other things to note

If the bot done goofed, the Nominations list txt file contains all names its scraped. Said file can be easily edited, preferably while the bot is paused.
