import smtplib
import re
from email.mime.text import MIMEText
import random
import sys
import imaplib
import email
import email.header
import configparser

punct = (".", ",", "!", "?")
conj = ("or", "but", "so")
letters_1 = ("f", "s", "c", "d", "n", "b")
letters_last2 = ("ck", "it", "ap", "mn", "er", "it")
smtp_ssl_host = 'smtp.gmail.com'
smtp_ssl_port = 465
config = configparser.ConfigParser()
config.read("settings.ini")
EMAIL_ACCOUNT = config["User data"]["user"]
EMAIL_PASSWORD = config["User data"]["pass"]
EMAIL_FOLDER = "inbox"
messages = []
seq_a = []
seq_b = []
outputseq = []
numtimes = config["Markov Chain settings"]["numtimes"]
chance = config["Markov Chain settings"]["chance"]

# My new generator uses this basic Markov chain.
def Markov(numtimes, chance):
    choice = 0
    for i in range(numtimes):
        num = random.randint(0, 100)
        if (num < chance):
            if (choice == 1):
                choice = 0
            else:
                choice = 1
    return choice

# This is an automatic email sending algorithm.
def sendEmail(mailTo, message, subj):
    username = EMAIL_ACCOUNT
    password = EMAIL_PASSWORD
    sender = username
    msg = MIMEText(message)
    msg['Subject'] = subj
    msg['From'] = sender
    msg['To'] = mailTo
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, mailTo, msg.as_string())
    server.quit()

# Maximum for my genetic algorithm.   
def maxi(listIn):
    i = 0
    maxindex = 0
    maximum = int(listIn[1])
    for i in range(len(listIn)):
        if (int(listIn[i]) > maximum):
            maximum = int(listIn[i])
            maxindex = i
        i += 1
    return maxindex

# Email receiving algorithm that processes my inbox.
def process_mailbox(M):
    rv, data = M.search(None, "ALL")
    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
        subject = str(hdr)
        messages.append(subject)

# Reads the raw HTML, and spits out an email.        
M = imaplib.IMAP4_SSL('imap.gmail.com')
try:
    rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
except imaplib.IMAP4.error:
    sys.exit(1)
rv, mailboxes = M.list()
rv, data = M.select(EMAIL_FOLDER)
if rv == 'OK':
    process_mailbox(M)
    M.close()
M.logout()
# Processing the raw input.
toProduce = messages[len(messages) - 1]
parsed = toProduce.split(" ")
email = ""
i = 1
for i in range(len(parsed)):
    if (i < len(parsed) - 1):
        email = email + parsed[i] + " "
    else:
        email = email + parsed[i]
    i += 1
# Parsing the email: Step 1
email_To_Split = email.lower()
emailuser = parsed[0]
splittedList = email_To_Split.split(" ")
splittedList.pop(0)
splittedList2 = splittedList

# Input/output tables for emails using if/then statements.
if ("file" in splittedList and "send" in splittedList):
    sendEmail(emailuser, "Will do soon.\nSincerely, Jacob Myers", "File")  
elif ("hi" in splittedList and "jacob!" in splittedList):
    sendEmail(emailuser, "Hi!\nSincerely, Jacob Myers", "Hi!")
elif ("how's" in splittedList and "going?" in splittedList and "it" in splittedList):
    sendEmail(emailuser, "I'm fine, thanks.\nSincerely, Jacob Myers", "Hi!")
elif ("you" in splittedList and "ok?" in splittedList):
    sendEmail(emailuser, "I'm fine, thanks.\nSincerely, Jacob Myers", "Hi")
elif ("i" in splittedList and "miss" in splittedList):
    if ("you" in splittedList):
        sendEmail(emailUser, "Here I am!\nSincerely, Jacob Myers", "Hi!")
    else:
        sendEmail(emailuser, "Who/what do you miss?\nSincerely, Jacob Myers", "Hi!")
elif ("i" in splittedList and "love" in splittedList and "you." in splittedList):
    sendEmail(emailuser, "I love you too.\nSincerely, Jacob Myers")
else:
    # Email algorithm v3: I revisited the genetic algorithm.
    # First iteration's random generator word extractor. It splits the raw email and removes any curses.
    i = 0
    email_To_Split = email.lower()
    email_To_Split2 = ""
    for i in range(len(email_To_Split)):
        if (not email_To_Split[i] in punct):
            email_To_Split2 = email_To_Split2 + email_To_Split[i]
        i += 1
    splittedList = email_To_Split2.split(" ")
    i = 0
    # Updating the .txt file with a fresh flow of words.
    text_file = open("stack.txt", "r")
    stack = text_file.read()
    parse = stack.split(" ")
    alteredStack = []
    i2 = 0
    words = ""
    eng_words = []
    values = open("english.txt", "r").readlines()
    for i in range(12):
        value = random.choice(values)
        if (not value in parse and not re.search("a|e|i|o|u+", value) == None and len(value) < 8):
            eng_words.append(value.replace("\n", ""))
    stack = stack + " ".join(eng_words)
    for i2 in range(len(splittedList)):
        curr = splittedList[i2]
        last2 = curr[len(curr) - 1] + curr[len(curr) - 2]
        if (not last2 in letters_last2 and not curr[0] in letters_1 and not curr in parse and re.search(".*@.*.com|.net|.edu", curr) == None):
            words = words + splittedList[i2] + " "
        i2 += 1
    stack = stack + words
    alteredStack = stack.split(" ")
    text_file = open("stack.txt", "w+")
    text_file.write(stack)
    text_file.close()
    splittedList.pop(len(splittedList) - 1)
    # Markov chain-based sequence generator.
    lenseq = random.randint(len(parsed), len(parsed) + 5)
    for i in range(lenseq):
        string1 = random.choice(alteredStack)
        string2 = random.choice(alteredStack)
        seq_a.append(string1)
        seq_b.append(string2)
        choice = Markov(int(numtimes), int(chance))
        if (choice == 0):
            outputseq.append(string1)
        else:
            outputseq.append(string2)
    # Then we just make the first letter capital and append a period to it, then send it.
    toSend = " ".join(outputseq).capitalize() + "."
    words = toSend.split(" ")
    subj = words[0].capitalize()
    sendEmail(emailuser, toSend.capitalize() + "\nSincerely, Jacob Myers", subj)
