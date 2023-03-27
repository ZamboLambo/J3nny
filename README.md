# Archive-Nombot
A Python script to automate parts of the job of tourney hosts on 4channel. 

# Setting up

1 -Download the current release "j3nny.dist.rar" and unzip it. (Compiled with nuitka, Windows only)

2 -Download the google api credentials. (see: https://automatetheboringstuff.com/2e/chapter14/ ->"Obtaining Credentials and Token Files")

3 -Place those files inside the folder where "j3nny.exe" is.

4 -Make sure you have Mozilla Firefox. 

5 -Make sure you are logged into your google account.

6 -Launch "j3nny.exe"

# About the bot

 Inputs needed: thread pattern to look for, board, name of google spreadsheet, minimum replies and link of almo.st timer.
 Runs until the current time is above the given timer or process is stopped.
 Updates the given spreadsheet with info scraped.
