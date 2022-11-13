# Archive-Nombot
A Python script to automate parts of the job of tourney hosts on 4channel. 

# Setting up

1 -Download "j3nny.rar" and unzip it. (To be added)

2 -Download the google api credentials. (see: https://automatetheboringstuff.com/2e/chapter14/ ->"Obtaining Credentials and Token Files")

3 -Place those files inside the folder where "j3nny.exe" is.

4 -Make sure you have Mozilla Firefox. 

5 -Make sure you are logged into your google account.

6 -Launch "j3nny.exe"

# About the bot

 It runs on a simple loop of going through the board's archive(specified by the user, sfw only), searching for threads with a link with the thread pattern(specified by the user), then if there's a match and the thread hasn't been looked through yet, analyzing the thread, or if not, sleeping for 10 minutes.
 
  For analyzing the thread it checks every post(after the OP), saving the ones that pass the checks. Checks consist of: must have an image, must have replies and the replies must be equal to or above the minimum(specified by the user). If all checks pass the bot tries to convert the post to fit "character( series)" appends it to "Nominations.txt" and moves to the next post.
  
  After all is done, the google sheet(specified by the user) is **wiped** and updated with the contents from "Nominations.txt". This update happens regardless of if it found a valid thread in the archive or not. Therefore if the bot messes up and misses a valid entry or outputs an invalid entry, the easiest way to fix it is **manually changing the _"Nominations.txt"_ file**. And if starting the bot on a sheet that already had content, archive the sheet first or move its contents to Nominations.txt.
