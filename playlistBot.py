import tweepy;
import pandas as pd
import re
import GetOldTweets3 as got
import sys
import jsonpickle
import os
import requests
import re
import urlmarker
import urlexpander

name = 'twitterPlaylist'

spotifyAuth = "BQDwTTsPaWmmT2xhM_WNBlmWIEIhm2f7Wjxq0CYT88gZSdquhzNSMILspqVU2npZoT3X_XOWeP_sEDbVTYOs913Pdb4nnR52pvDdYQ5qeZYrLAgAxnpqNBJgVvn1Zwm9BV3plj_pGH9fZA5weIdKyAoTYz23xFkao5dWDmTJFCn4g1BSGKVDyScX_FhMXE9_dYA"

auth = tweepy.AppAuthHandler("7O7X2Gs8XtsmZc3pESOp0UAij", "xhgtSw8ovaCKhR3gi7AlYTuvRGq7heAbzUpUJJvcrpeM3WY2gt")

consumer_key= '7O7X2Gs8XtsmZc3pESOp0UAij'
consumer_secret= 'xhgtSw8ovaCKhR3gi7AlYTuvRGq7heAbzUpUJJvcrpeM3WY2gt'
access_token= '1230058983253331968-9UIqplP5aUWP51hrc4WSO3Pa0nTqhu'
access_token_secret= 'h0YXsYbqrn5Unt6M6gTl8I07ZmBtWycaqITcofxORoqyj'

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

userAccount = input("Enter Twitter Account to Scan Without The @ Symbol: ")

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

def clean_tweet(tweet): 
    ''' 
    Utility function to clean tweet text by removing links, special characters 
    using simple regex statements. 
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 

def getUri(url):
    if "track" in url:
        code = url.split('/track/')[1]
        songCode = code.split('?')[0]
        uri = "spotify:user:"+songCode
        return uri
    else:
        return None

searchQuery = 'url:spotify lang:en from:'+userAccount+' @'+userAccount  # this is what we're searching for
maxTweets = 500 # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits

sinceId = None

max_id = -1
tweet_list = []    
tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
while tweetCount < maxTweets:
    try:
        if (max_id <= 0):
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, tweet_mode='extended')
            else:
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, since_id=sinceId, tweet_mode='extended')
        else:
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), tweet_mode='extended')
            else: new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId, tweet_mode='extended')
        if not new_tweets:
            print("No more tweets found")
            break
        for tweet in new_tweets:
            tweet_list.append(tweet.full_text)
            #print(tweet.full_text)
            print(tweet.url)
        tweetCount += len(new_tweets)
        print("Found {0} tweets".format(tweetCount))
        max_id = new_tweets[-1].id
    except tweepy.TweepError as e:
           # # Just exit if any error
        print("some error : " + str(e))
        break
    
print ("Downloaded {0} tweets.".format(tweetCount))

for tweet in tweet_list:
    songUrls = re.findall(urlmarker.URL_REGEX, tweet)
    #songUrls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tweet)
    for songUrl in songUrls:
        print(songUrl)
        expanded = urlexpander.expand(songUrl)
        print(expanded)
        if "spotify" in songUrl:
            songUri = getUri(songUrl)
            if songUri is not None:
                print("added a song!")
                requests.post("https://api.spotify.com/v1/playlists/34PelCJCvwUvOQIbhoN0he/tracks?uris="+songUri+" Accept: application/json"+" Content-Type: application/json"+" Authorization: Bearer "+spotifyAuth)
                print("added a song!3223123123")
        else:
            print("not a track, can't add!")
