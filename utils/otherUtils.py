'''
Imports
'''
import os
import numpy as np
import string


def addFullPath(fileName, pathToImages):
    fileName = (str(fileName) + '.jpg')
    return os.path.join(pathToImages, fileName)

def calcZeroBaseline(count_fake, count_not_fake):
    count_total = count_fake + count_not_fake
    bigger_class = None
    if count_fake >= count_not_fake:
        bigger_class = count_fake
    else:
        bigger_class = count_not_fake
    print("The zero baseline for this set is: " + str(round((bigger_class * 100)/count_total)) + "%. ")

def chunkify(lst,n):
    return [ lst[i::n] for i in range(n) ]  

def convertRowToDictionary(row, columns, hasIndex = False):
    dict = {}
    for idx, col in enumerate(columns):
        if hasIndex:
            dict['index'] = row[idx]
        dict[col] = row[idx + 1]
    return dict
    
def isBlank(myString):
    return not (myString and myString.strip())

def parseStringAsNpArray(string):
    return np.fromstring(string[1:-1], dtype=np.float, sep=' ')

def processComment(comment):
    exclude = set(string.punctuation)
#     exclude.append()
    
    comment = str(comment).rstrip('\n')
    comment = ''.join(ch for ch in comment if ch not in exclude)
    comment = comment.translate({ord(ch): None for ch in '0123456789'})
    comment = comment.lower()
    comment = str(comment).rstrip('\n')
    
    return comment