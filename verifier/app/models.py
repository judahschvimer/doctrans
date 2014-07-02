import datetime
from pymongo import MongoClient

mongodb = MongoClient()


def get_sentence():
    sentence = mongodb['veri']['translations'].find_one({"approved":False})
    return sentence
'''
    for sentence in translations:  
        t = Translation()
        t.ingest(sentence)
        yield t
'''
class Sentence(object):
    def __init__(self):
        self.state = {'created_at' : datetime.datetime.utcnow(), 'username': None, 'source_language': None, 'source_sentence':None, 'sentence_num': -1, 'file_path': None, 'sentenceID': None, 'target_sentence': None, 'status': 'init', 'update_number': 0, 'target_language': None} 

    def ingest(self, state):
        for k,v in state.iteritems():
            if not self.state.has_key(k):
                return 1
        if self.state['status']!='init': archive()
        for k,v in state.iteritems():
            self.state[k]=v
        return 0

    def save(self): 
        mongodb['veri']['translations'].save(self.state)
    
    def archive(self):
        mongodb['veri']['archive'].save(self.state)
        self.state['update_number']=self.state['update_number']+1

    @property
    def target_language(self):
        return self.state['target_language']
     
    @property
    def source_language(self):
        return self.state['source_language']
    
    @property
    def username(self):
        return self.state['username']
    
    @property
    def status(self):
        return self.state['status']
    
    @property
    def file_path(self):
        return self.state['file_path']
    
    @property
    def create_at(self):
        return self.state['created_at']
    
    @property
    def source_sentence(self):
        return self.state['source_sentence']
 
    @property
    def target_sentence(self):
        return self.state['target_sentence']  
    
    @target_language.setter
    def target_language(self, value): 
        if value in ('es', 'jp', 'cz'): 
           self.state['target_language']=value
        else: 
           raise TypeError    

class User(object):
    def __init__(self):
        self.state = {'username': None, 'num_translated': 0, 'num_approved' : 0}

    def increment_translated(self):
        self.state['num_translated']=self.state['num_translated']+1

    def increment_approved(self):
        self.state['num_approved']=self.state['num_approved']+1

    @property
    def username(self):
        return self.state['username']  

    @property
    def num_translated(self):
        return self.state['num_translated']  
    
    @property
    def num_approved(self):
        return self.state['num_approved']  
    
    def save(self): 
        mongodb['veri']['users'].update({'username':self.state['username']}, {'$set':{'num_translated':self.state['num_translated'], 'num_approved':self.state['num_approved']}},upsert=True)