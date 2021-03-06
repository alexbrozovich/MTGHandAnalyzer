from __future__ import division
import csv
import operator
import numpy as np
import statsmodels.api as sm
import matplotlib
import pandas
import itertools
from sklearn import linear_model
from scipy import stats
from matplotlib import pyplot as plt

##takes in the usual stuff
##returns two different models for regression analysis
##needs to be split into different methods for different models
##maybe try argument that determines which of the models is returned?
def regressionAnalysis(cardDict, handsFromDeck, winLoss, uniqueCards):
    i = 0
    aliasDict = {}
    translatedHands = []
    uniqueCards.append("")
    winLossBool = []
    for item in winLoss:
        if (item.upper() == "WIN" or item.upper() == "WON"):
            winLossBool.append(1)
        else:
            winLossBool.append(0)
    while (i < len(uniqueCards)):
           aliasDict[uniqueCards[i].upper()] = i
           i += 1
    for line in handsFromDeck:
        currentTranslatedHand = [0] * len(aliasDict)
        for item in line:
            currentTranslatedHand[aliasDict[item.upper()]] += 1
        translatedHands.append(currentTranslatedHand)
    OGX = np.stack((translatedHands))
    newX = sm.add_constant(OGX)
    newR = sm.OLS(winLossBool, newX).fit()

    ##reg = linear_model.LinearRegression()
    ##reg = linear_model.Ridge()
    reg = linear_model.Lasso()
    reg.fit(OGX, winLossBool)
    return newR, reg, aliasDict

##takes in two models and a hand for evaluation 
##returns the percentage predictions for the two different models
##same as regressionAnalysis(), needs to be split up to only return one at a time
##argument that flags whether the passed model is sklearn or statsmodels
def evaluateHand(model, scimodel, singleHand, aliasDict):
    currentTranslatedHand = [0] * len(aliasDict)
    for item in singleHand:
        currentTranslatedHand[aliasDict[item.upper()]] += 1
    i = 0
    predictedOutcome = model.params[0]
    while (i < len(aliasDict)):
        predictedOutcome += currentTranslatedHand[i] * model.params[i+1]
        i += 1
    scipredict = scimodel.predict([currentTranslatedHand, currentTranslatedHand])
    return predictedOutcome, scipredict
    
##open the csv file with opening hands and create an array from them
def createData(filename, permissions):
    handHolder = []
    with open(filename, permissions) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            handHolder.append(row)
    return handHolder


def writeCSV(filename, permissions, header, rows_to_write):
    with open(filename, permissions) as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(header)
        for item in rows_to_write:
            writer.writerow(item)
        
        
##takes in the array of wins and losses in text
##returns total wins and total losses as integers
def getWinsLosses(winLoss):
    wins = 0
    losses = 0
    for item in winLoss:
        if (item.upper() == "WIN" or item.upper() == "WON"):
            wins += 1
        else:
            losses += 1
    return wins, losses

##takes in cardDict and an array of all opening hands
##returns cardDict with the total number of opening hands at position 0 for each card
def getHandsWithCards(cardDict, handsFromDeck):
    for line in handsFromDeck:
        hasCard = 0
        alreadyFound = []
        for item in line:
            if (item != "" and item.upper() not in alreadyFound):
                cardDict[item.upper()][0] += 1
                alreadyFound.append(item.upper())
    return cardDict

##takes in cardDict along with list of hands and wins/losses
##returns cardDict with win % with hands from that card
def getWinsWithCards(cardDict, handsFromDeck, winLoss):
    i = 0
    for line in handsFromDeck:
        for item in line:
            if (winLoss[i].upper() == "WIN" or winLoss[i].upper() == "WON"):
                if (item != ""):
                    cardDict[item.upper()][1] += 1
            else:
                if (item != ""):
                    cardDict[item.upper()][2] += 1
        i += 1
    for item in cardDict:
        if (cardDict[item][2] != 0):
            cardDict[item][3] = round(long(cardDict[item][1])/(long(cardDict[item][1])+long(cardDict[item][2])),4)*100
        else:
            cardDict[item][3] = 100.00
    return cardDict
                         
def printStats(chosenDeck, handsFromDeck, winLoss, uniqueCards, printStuff, exportStuff):
    wins, losses = getWinsLosses(winLoss)
    winPercentage = long(wins) / (long(wins)+long(losses))
    ##0: number of hands with that card
    ##1: wins for hands with that card
    ##2: losses for hands with that card
    ##3: win % for hands with that card
    cardDict = {}
    for item in uniqueCards:
        cardDict[item] = [0,0,0,0]
    cardDict = getHandsWithCards(cardDict, handsFromDeck)
    cardDict = getWinsWithCards(cardDict, handsFromDeck, winLoss)
    commonHands = sorted(cardDict.items(), key=operator.itemgetter(1), reverse=True)
    commonHandPretty = []
    commonHandRows = []
    winningHandRows = []
    winsByMullRows = []
    winningHands = {}
    for item in commonHands:
        winningHands[item[0]] = item[1][3]
    winningHandsSorted = sorted(winningHands.items(), key=operator.itemgetter(1), reverse=True)
    for item in commonHands:
        commonHandPretty.append([item[0],round(long(item[1][0])/long(len(handsFromDeck)),4)*100])
    for item in commonHandPretty:
        ##print item[0] + ": " + str(item[1]) + "%"
        commonHandRows.append([item[0],str(item[1])+"%\n"])
    winningHandsSortedPrinter = ""
    for item in winningHandsSorted:
        plusMinus = ""
        relWin = cardDict[item[0]][3] - (winPercentage * 100)
        if relWin < 0:
            plusMinus = "-"
        else:
            plusMinus = "+"
        winningHandsSortedPrinter += item[0] + ": " + str(item[1]) + "%, " + str(cardDict[item[0]][0]) + ", " + plusMinus + str(round(abs(relWin),2)) + "%" + "\n"
        winningHandRows.append([item[0],str(item[1])+"%",str(cardDict[item[0]][0]),plusMinus + str(round(abs(relWin),2))+"%\n"])
    totalMulls = 0
    for line in handsFromDeck:
        didMull = 0
        for item in line:
            if item == "":
                 didMull = 1
        totalMulls += didMull
    winsByMull = [0,0,0,0,0,0,0,0]
    gamesByMull = [0,0,0,0,0,0,0,0]
    i = 0
    for line in handsFromDeck:
        numMulls = 0
        for item in line:
            if item == "":
                numMulls += 1
        if (winLoss[i].upper() == "WIN" or winLoss[i].upper() == "WON"):
            winsByMull[numMulls] += 1
        gamesByMull[numMulls] += 1
        i += 1
    i = 0
    winsByMullPrinter = ""
    while (i < 8):
        if (gamesByMull[i] == 0):
            winsByMullPrinter += str(i) + ": 0%, " + str(gamesByMull[i]) + "\n"
            winsByMullRows.append([str(i),"0", gamesByMull[i]])
        else:
            winsByMullPrinter += str(i) + ": " + str(round(float(winsByMull[i])/float(gamesByMull[i]),4)*100) + "%, " + str(gamesByMull[i]) + "\n"
            winsByMullRows.append([str(i), str(round(float(winsByMull[i])/float(gamesByMull[i]),4)*100) + "%", gamesByMull[i]])
        i += 1
    regressionModel, newReg, aliasDict = regressionAnalysis(cardDict, handsFromDeck, winLoss, uniqueCards)
    testHand = ['bloodstained mire', 'sacred foundry', 'lingering souls', 'fatal push', 'bedlam reveler', '']
    testHand2 = testHand
    chanceToWin, sciChance = evaluateHand(regressionModel, newReg, testHand, aliasDict)
    if (printStuff == True):
        print "Deck: ".upper() + chosenDeck
        print "Overall Game Win Percentage: " + str(round(winPercentage, 4)*100) + "%"
        print "Total Games Played: " + str(len(handsFromDeck))
        print "\n"
        print "Cards sorted by % of kept hands that contain them:".upper()
        for item in commonHandPretty:
            print item[0] + ": " + str(item[1]) + "%"
        print "\n"
        print "Cards sorted by win % of hands that contain them, total # of hands, +/- average win %:".upper()
        print winningHandsSortedPrinter
        print "\n"
        print "% of games with > 0 mulligans:"
        print round(long(totalMulls) / long(len(handsFromDeck)),4)*100
        print "\n"
        print "Win % by # of mulligans, # of games with # of mulligans: "
        print winsByMullPrinter
        print chanceToWin
        print sciChance[0]
        print regressionModel.summary(xname=(["CONSTANT"]+uniqueCards))

    if (exportStuff == True):
        writeCSV("percentHands.csv", "wb", ["CARD NAME","% OF KEPT HANDS CONTAINING\n"], commonHandRows)
        writeCSV("winPercentHands.csv", "wb", ["CARD NAME","WIN % OF CONTAINING HANDS", "TOTAL # OF HANDS CONTAINED IN", "+/- AVERAGE WIN %\n"], winningHandRows)
        writeCSV("mullWinPercent.csv", "wb", ["# OF MULLIGANS TAKEN", "WIN %", "GAMES WITH X MULLIGANS"], winsByMullRows)
    
    
def mainFunction():
    chosenDeck = "MARDU PYROMANCER"
    handList = createData("handData.csv", 'rb')
    printStuff = True
    exportStuff = False

    ##takes all hands of chosenDeck and adds them to handsFromDeck 
    handsFromDeck = []
    winLoss = []
    for line in handList:
        if (line[2].upper() == chosenDeck):
            handsFromDeck.append(line[-7:])
            winLoss.append(line[5])
            
    ##creates list of unique cards across all hands from chosenDeck in spreadsheet
    uniqueCards = []
    for line in handsFromDeck:
        for item in line:
            if item.upper() not in uniqueCards:
                if (item != ""):
                    uniqueCards.append(item.upper())
    printStats(chosenDeck, handsFromDeck, winLoss, uniqueCards, printStuff, exportStuff)
    
mainFunction()
    

