#!/usr/bin/python
import json
import flask
import re
import pyodbc
import requests
from flask import Flask, jsonify, request
import bs4
#from bs4 import BeautifulSoup
from werkzeug.exceptions import Forbidden, HTTPException, NotFound, RequestTimeout, Unauthorized
from urllib.parse import urlparse

#Publish command: az webapp up --sku F1 -n csi4999webcat
#This does not import modules! Use Git push to force module import. 

app = flask.Flask(__name__)
#app.config["DEBUG"] = True

#@app.errorhandler(NotFound)
#def page_not_found_handler(e: HTTPException):
#    return render_template('404.html'), 404


#@app.errorhandler(Unauthorized)
#def unauthorized_handler(e: HTTPException):
#    return render_template('401.html'), 401


#@app.errorhandler(Forbidden)
#def forbidden_handler(e: HTTPException):
#    return render_template('403.html'), 403


#@app.errorhandler(RequestTimeout)
#def request_timeout_handler(e: HTTPException):
#    return render_template('408.html'), 408


@app.route('/post', methods=['GET', 'POST'])
def parse():

    #Database parameters
    server='webcatcsi4999.database.windows.net'
    database='webcat'
    username='webcat'
    password='Connect123!'
    driver='{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

    #Variable Setup
    rankingValue = 0
    rankingName = ''
    matchCount = 1
    inputWordList = []
    inputWordValues = []
    exclusionWordList = []

    #Top contributing words, to be turned into top phrases
    topWordList = []
    topWordValues = []
    topWordList.append('none')
    topWordValues.append(0)

    #Retreive input word list from DB
    inputWordTable = cnxn.cursor()
    inputWordTable.execute("SELECT * FROM WordList")
    inputWord = inputWordTable.fetchone()
    while inputWord:
        inputWordList.append(str(inputWord[1]))
        inputWordValues.append(str(inputWord[2]))
        inputWord = inputWordTable.fetchone()

    #print (inputWordList)
    #print (inputWordValues)

    inputWordTable.close()

    #Retreive exclusion word list from DB
    exclusionWordTable = cnxn.cursor()
    exclusionWordTable.execute("SELECT * FROM ExclusionList")
    exclusionWord = exclusionWordTable.fetchone()
    while exclusionWord:
        exclusionWordList.append(str(exclusionWord[1]))
        exclusionWord = exclusionWordTable.fetchone()

    #print (exclusionWordList)

    exclusionWordTable.close()
    cnxn.close()

    #Scrape Article
    url =  request.args.get('url') # http://127.0.0.1:5000/post?url=[param]

    payload = {'api_key': 'f11d7c6f3e7dacf16f168f8fd058c3c8', 'url': url}

    r = requests.get('http://api.scraperapi.com', params=payload)
    
    html = bs4.BeautifulSoup(r.content, "html.parser")
   
    articleData = []

    for p in html.find_all('p'):
        text_object = p.text.encode()
        text = text_object.decode()
        sentences = {'sentence' : text.replace('\n', ''),}
        articleData.append(sentences)

    # Pretty Print JSON data
    #print(json.dumps(articleData, indent = 4, sort_keys=True))

    #Check if ranked words are in article data and record in top list
    for sentence in articleData:

        for inputWord in inputWordList:

            index = inputWordList.index(inputWord)
            
            match = re.search(inputWord, str(sentence), re.IGNORECASE)

            if match:

                matchCount = matchCount + 1
                value = int(inputWordValues[index])
                rankingValue += value

                absolute = abs(value)

                for topWord in topWordList:
                        topIndex = topWordList.index(topWord)
                        topValue = int(topWordValues[topIndex])
                        
                        if absolute >= topValue:
                            topWordList.insert(topIndex,inputWord)
                            topWordValues.insert(topIndex,absolute)

                            if len(topWordList) == 11:
                                topWordList.pop(10)
                                topWordValues.pop(10)

                            break

    #Sort list in descending order to list top contributing words
    topWordList.sort(key=dict(zip(topWordList,topWordValues)).get, reverse=True)

    #Add weighted URL-word based on news source, if appears biased on allsides.com
    parsedURL = urlparse(url)

    print (parsedURL.netloc)

    if re.search("abcnews.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (ABC News)")
        topWordValues.insert(0,250)
    elif re.search("alternet.org",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Alternet)")
        topWordValues.insert(0,250)
    elif re.search("spectator.org",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (American Spectator)")
        topWordValues.insert(0,250)
    elif re.search("breitbart.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (Brietbart)")
        topWordValues.insert(0,250)
    elif re.search("buzzfeednews.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Buzzfeed News)")
        topWordValues.insert(0,250)
    elif re.search("cbsnews.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (CBS News)")
        topWordValues.insert(0,250)
    elif re.search("cnn.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (CNN)")
        topWordValues.insert(0,250)
    elif re.search("thedailybeast.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (The Daily Beast)")
        topWordValues.insert(0,250)
    elif re.search("dailymail.co.uk",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (Daily Mail)")
        topWordValues.insert(0,250)
    elif re.search("democracynow.org",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Democracy Now)")
        topWordValues.insert(0,250)
    elif re.search("foxnews.com",parsedURL.netloc) is not None:
        rankingValue += 250
        topWordList.insert(0,"Souce Bias (Fox News)")
        topWordValues.insert(0,250)
    elif re.search("huffpost.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Huff Post)")
        topWordValues.insert(0,250)
    elif re.search("motherjones.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Mother Jones)")
        topWordValues.insert(0,250)
    elif re.search("msnbc.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (MSNBC)")
        topWordValues.insert(0,250)
    elif re.search("nationalreview.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (National Review)")
        topWordValues.insert(0,250)
    elif re.search("nbcnews.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (NBC News)")
        topWordValues.insert(0,250)
    elif re.search("nypost.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (NY Post)")
        topWordValues.insert(0,250)
    elif re.search("nytimes.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (NY Times)")
        topWordValues.insert(0,250)
    elif re.search("npr.org",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (NPR)")
        topWordValues.insert(0,250)
    elif re.search("politico.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (Politico)")
        topWordValues.insert(0,250)
    elif re.search("reason.com",parsedURL.netloc) is not None:
        rankingValue += 250
        topWordList.insert(0,"Souce Bias (Reason)")
        topWordValues.insert(0,250)
    elif re.search("slate.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Slate)")
        topWordValues.insert(0,250)
    elif re.search("dailycaller.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (The Daily Caller)")
        topWordValues.insert(0,250)
    elif re.search("dailywire.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (The Daily Wire)")
        topWordValues.insert(0,250)
    elif re.search("economist.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (The Economist)")
        topWordValues.insert(0,250)
    elif re.search("thefederalist.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (The Federalist)")
        topWordValues.insert(0,250)
    elif re.search("theguardian.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (The Guardian)")
        topWordValues.insert(0,250)
    elif re.search("theintercept.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (The Intercept)")
        topWordValues.insert(0,250)
    elif re.search("newyorker.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (The New Yorker)")
        topWordValues.insert(0,250)
    elif re.search("theblaze.com",parsedURL.netloc) is not None:
        rankingValue += 500
        topWordList.insert(0,"Souce Bias (The Blaze)")
        topWordValues.insert(0,250)
    elif re.search("time.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (Time)")
        topWordValues.insert(0,250)
    elif re.search("vox.com",parsedURL.netloc) is not None:
        rankingValue += -500
        topWordList.insert(0,"Souce Bias (Vox)")
        topWordValues.insert(0,250)
    elif re.search("wsj.com",parsedURL.netloc) is not None:
        rankingValue += 250
        topWordList.insert(0,"Souce Bias (Wall Street Journal)")
        topWordValues.insert(0,250)
    elif re.search("washingtonexaminer.com",parsedURL.netloc) is not None:
        rankingValue += 250
        topWordList.insert(0,"Souce Bias (Washington Examiner)")
        topWordValues.insert(0,250)
    elif re.search("washingtonpost.com",parsedURL.netloc) is not None:
        rankingValue += -250
        topWordList.insert(0,"Souce Bias (Washington Post)")
        topWordValues.insert(0,250)
    elif re.search("washingtontimes.com",parsedURL.netloc) is not None:
        rankingValue += 250
        topWordList.insert(0,"Souce Bias (Washington Times)")
        topWordValues.insert(0,250)

    #Assign categorization rank

    #Far Right  +100 to +75
    #Right       +75 to +50
    #Lean Right  +50 to +25
    #Neutral     +25 to -25
    #Lean Left   -25 to -50
    #Left        -50 to -75
    #Far Left    -75 to -100

    rankingRange = (matchCount * 2 * 50)

    rankingPercent = (int((rankingValue / rankingRange) * 100))

    print ("matchCount: ", matchCount)
    print ("rankingRange: ", rankingRange)
    print ("rankingValue: ", rankingValue)
    print ("rankingPercent: ",rankingPercent)

    if (rankingPercent <= 100 and rankingPercent > 75):
        rankingName = 'FarRight'

    elif (rankingPercent <= 75 and rankingPercent > 50):
        rankingName = 'Right'

    elif (rankingPercent <= 50 and rankingPercent > 25):
        rankingName = 'LeanRight'

    elif (rankingPercent <= 25 and rankingPercent >= -25):
        rankingName = 'Neutral'

    elif (rankingPercent < -25 and rankingPercent >= -50):
        rankingName = 'LeanLeft'

    elif (rankingPercent < -50 and rankingPercent >= -75):
        rankingName = 'Left'

    elif (rankingPercent < -75 and rankingPercent >= -100):
        rankingName = 'FarLeft'

    if matchCount < 10:
        rankingName = 'Undetermined'

    #Return rank and top word list
    print(rankingName, topWordList)
    return jsonify(rankingName, topWordList)

#app.run(host='0.0.0.0',port="8000")
app.run()
