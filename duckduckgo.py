'''
Created on Apr 17, 2016

@author: ohad
'''
from urllib2 import urlopen
from json import loads as parseJson
from subprocess import Popen, PIPE
from thread import allocate_lock

curl=Popen(['php', 'req.php'], stdin = PIPE, stdout = PIPE)
LAST_LENGTH = 0
complition_lock = allocate_lock()
ERROR_SIZES = [382, 31]
def getCompletionLength(prefix, tryies=3):
#     response = urlopen('https://www.google.co.il/complete/search?client=hp&hl=iw&gs_rn=64'+
#                        '&gs_ri=hp&cp=2&gs_id=18w&xhr=t&tch=1&ech=3&psi=MpwTV8enJKbJ6ASilqaoDg.1460902971738.1'+
#                        '&q=' + prefix)
    complition_lock.acquire()
    curl.stdin.write(prefix + '\n')
    curl.stdout.readline()
    ret = LAST_LENGTH
    if ret in ERROR_SIZES and tryies:
        return getCompletionLength(prefix, tryies-1)
    complition_lock.release()
    return ret
    response = urlopen('https://ac.duckduckgo.com/ac/?callback=autocompleteCallback&_=1461001571433&q='+prefix)
    resptext = response.read()
#     print(resptext)
    try:
        return response.headers['content-length']
    except:
        return len(resptext)

def getCompletionArray(word):
    response = urlopen('https://ac.duckduckgo.com/ac/?q='+word.replace(' ', '%20'))
    data = response.read().replace('autocompleteCallback(', '').replace(');', '')
    array = [d['phrase'] for d in parseJson(data)]
    return array
