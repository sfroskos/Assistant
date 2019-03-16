#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 11:28:41 2018

@author: seth roskos
"""
import spacy
from spacy.symbols import nsubj, VERB
from googlesearch import search 

# Load SpaCy Natural Language Processing English Language Module
nlp = spacy.load('en_core_web_md')

#Get root verb from user input
def getrootverb(doc):
    for possible_root in doc:
        if possible_root.dep_ == 'ROOT' and possible_root.pos_ == 'VERB':
            return possible_root

#Get subject noun chunk for root verb
def getsubject(doc):
    for chunk in doc.noun_chunks:
        if chunk.root.dep_=='nsubj':
            return chunk

#Get object of root verb noun chunk
def getobject(doc,root):
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ == 'nobj' and chunk.root == root:
                return chunk
        
#Get preposition modifying root verb from user input
def getprep(doc,root):
    for token in doc:
        if token.pos == 'ADP' and token.root == root:
            return token.text

#Get object for preposition modifying root verb from user input
def getprepobj(doc,prep):
    for token in doc:
        if token.pos == 'pobj' and token.head == prep:
            return token.text

def analyzeuserinput(userinput):
#Run NLP against user request and create a dictionary of key grammatical components
    doc = nlp(userinput['text'])
    #Print all part of speech tagging
    print('Print all part of speech tagging')
    for token in doc:
        print(token.text, token.lemma_, token.head.text, token.pos_, token.tag_, token.dep_,token.shape_, token.is_alpha, token.is_stop)
    #Pull key sentence components to create a response
    userinput['verb'] = getrootverb(doc)
    userinput['subject'] = getsubject(doc)
    userinput['object'] = getobject(doc,userinput['verb'])
    userinput['prep'] = getprep(doc,userinput['verb'])
    userinput['prepobj'] = getprepobj(doc,userinput['verb'])
    print('UsreInput after analyzeuserinput')
    print(userinput)
    return userinput

#Looks like it is not a fully formed request but maybe a brief response to our last query
def confirmintent(responsetext):
    responselist = stringtolist(responsetext)
    righttracklist = ['yes','please','correct','right','sure','ok','okay']
    wrongtracklist = ['no','not','wrong','incorrect','idiot','damnit']
    tries = 0
    while tries < 4:
        for word in responselist:
            if word.lower() in righttracklist:
                return True
            elif word.lower() in wrongtracklist:
                return False
            else:
                tries = tries + 1
                responselist = stringtolist(getuserinput("Sorry I'm still not quite clear. Please try to clarify for me. Yes or No works well: "))
                print('tries = ' + str(tries))
    return False        

#confirm that we have understood the users request by repeating it back and asking for confirmation
def confirmrequest(request):
    if checkforrequest(request):
        if request['prep']:
            assistantresponse = 'So you would like to ' + request['verb'].text + ' '+ request['prep'].text + ' ' + request['object'].text + '?'
        elif request['object']:
            assistantresponse = 'So you would like to ' + request['verb'].text + ' ' +  request['object'].text + '?'
        else:
            assistantresponse = 'So you would like to ' + request['verb'].text + '?'
        userinput = getuserinput(assistantresponse)
        if confirmintent(userinput):
            print("Glad I'm on the right track.")
            request['flag'] = True
        else:
            request['flag'] = False
    else:
        request['flag'] = False    
    return request
 
#Check to see if this is a request or a response based on the existence of key sentence components
def checkforrequest(request):
    if request['verb'] and request['subject']:
        return True
    else:
        return False

#Function to get user input
def getuserinput(cue):
    return input(cue)

#Function to convert a string to a list
def stringtolist(string):
    return list(string.split(' '))

#Ask for another question when the assistant misunderstands the user
    #Moved this code to main for clarity
def misunderstood():
    userinput = getuserinput("Sorry. I am not quite understanding. Would you like to try another question? Maybe I'll understand better if you re-phrase the question: ")
    request = analyzeuserinput(userinput)
    if confirmrequest(request):
        userinput = getuserinput('What else would you like to know?')
        return False
    else:
        print("I'm sorry I couldn't help more. Maybe next time.")
        return True
    
#Use the request to determine an appropriate response with the information requested
def createresponse(request):
    return True
    
#If the requested information is not in the assistant's knowledge domain search the web
def websearch(query):  
    print('Unfortunately that request is not within my primary knowledge domain. Below are some web sites tha might help:')
    for url in search(query, tld="com", num=5, stop=1, pause=2): 
        print(url)

# Solicit question from user to analyze
userinput = dict.fromkeys(['text','flag','subject','object','verb','prep','prepobj'])
request = userinput
userinput['text'] = getuserinput('What would you like to know?')
goodconvo = True
while goodconvo and userinput['text'].lower != 'quit':
    print(goodconvo)
    request = analyzeuserinput(userinput)
    confirmedrequest = confirmrequest(request)
    goodconvo = confirmedrequest['flag']
    if not goodconvo:
        userinput['text'] = getuserinput("Sorry. I am not quite understanding. Would you like to try another question? Maybe I'll understand better if you re-phrase the question: ")
        request = analyzeuserinput(userinput)
        confirmedrequest = confirmrequest(request)
        if not confirmedrequest['flag']:
            userinput['text'] = getuserinput('What else would you like to know?(type quit to end the discussion)')
            goodconvo = True
        else:
            print("I'm sorry I couldn't help more. Maybe next time.")
            goodconvo = False    
    elif not createresponse(request):
       websearch(request['text'])
       userinput['text'] = getuserinput('What else would you like to know?(type quit to end the discussion)')
        
    

