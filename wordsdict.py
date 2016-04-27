'''
Created on Apr 19, 2016

@author: ohad
'''
from difflib import get_close_matches
from thread import start_new_thread, allocate_lock
import pickle
from os.path import isfile
from string import lowercase, digits
from time import sleep
from logging import getLogger, INFO, basicConfig as loggerConfig
from duckduckgo import getCompletionArray, getCompletionLength

logger = getLogger(__name__)


class WordsDict():
    def __init__(self, initlen = 3, chars = lowercase + digits, db_file = None):
        self.chars = chars
        self.filename = db_file
        self.block = 0
        self.save_lock = allocate_lock()
        self.sug_dict = {}

        if db_file and isfile(db_file):
            try:
                with open(db_file, 'rb') as db:
                    self.sym_dict = pickle.load(db)
                    self.num_dict = pickle.load(db)
            except:
                pass
        if not hasattr(self,'sym_dict'):
            self.sym_dict = {}
            self.num_dict = {}
            start_new_thread(self.make_db, ('', 1, initlen, True))
        
    def add_word_db(self, word):
        res = getCompletionLength(word)
        self.sym_dict[word] = res
        if not self.num_dict.get(self.sym_dict[word]):
            self.num_dict[self.sym_dict[word]] = []
        self.num_dict[self.sym_dict[word]].append(word)
        logger.debug('letter %s added to DB, length %d'%(word, self.sym_dict[word]))
        
    def make_db(self, s, n, N, save = False):
        if save:
            self.block += 1
            logger.info('adding letters to DB, start with %s from %s to %d chars'%(s, n, N))
        # base case:
        if len(s) == n:
            try:
                self.add_word_db(s)
                if not len(self.sym_dict)%100:
                    logger.info('%s words in dict'% len(self.sym_dict))
            except Exception as e:
                logger.info('need a break on %s reason %r'%(s, e))
                sleep(60)
                self.make_db(s, n, N)
            if n < N:
                self.make_db(s, n+1, N)
        else:
            for let in self.chars:
                new_str = s + let
                self.make_db(new_str, n, N)
        if save:
            self.block -= 1
        if save and self.filename:
            self.save(self.filename)
    
    def __get__(self, query):
        if isinstance(query, str):
            return self.sym_dict[query]
        elif isinstance(query, int):
            return self.num_dict[query]
        
    def load_sugestions(self, word):
        logger.info('adding suggestions of %s to DB'%word)
        self.block += 1
        try:
            self.sug_dict[word] = getCompletionArray(word)
        except:
            self.block -= 1
            return
        for sug in self.sug_dict[word]:
            try:
                self.add_word_db(sug)
            except:
                pass
        self.block -= 1
        if self.filename:
            self.save(self.filename)
        
    def getSimilar(self, packet_length, prefix):
        ret = get_close_matches(prefix, self.num_dict[packet_length])
        if not ret:
            ret = [s for s in self.num_dict[packet_length] if s.startswith(prefix)]
        if not ret:
            ret = [s for s in self.num_dict[packet_length] if prefix.startswith(s)]
        if not ret:
            ret = [s for s in self.num_dict[packet_length] if s in self.sug_dict[prefix]]
        for word in ret:
            if not self.sug_dict.get(word):
                l = len(word)
                start_new_thread(self.make_db, (word, l, l + 1, True))
                start_new_thread(self.load_sugestions, (word,))
        return ret
    
    def save(self, filename):
        self.save_lock.acquire()
        with open(filename, 'wb') as handle:
            pickle.dump(self.sym_dict, handle)
            pickle.dump(self.num_dict, handle)
        self.save_lock.release()
        logger.info('wordsdb saved to ' + filename)

if __name__ == '__main__':
    loggerConfig(level=INFO, format='%(asctime)s - %(levelname)s - pid:%(process)d - %(message)s')
    mydict = WordsDict(db_file='lengths.pickle')
    sleep(60)
    while mydict.block:
        sleep(60)
    
