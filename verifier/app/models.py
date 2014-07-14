import datetime
from pymongo import MongoClient
import logging
from . import app

logger = logging.getLogger('models')
logging.basicConfig(level=logging.DEBUG)

mongodb = MongoClient('localhost', 28000)

def get_sentences_in_file(fp, source_language, target_language):
    logger.debug(fp)
    file = mongodb['veri']['files'].find_one({'source_language': source_language, 
                                              'target_language': target_language, 
                                              'file_path': fp}, 
                                             {'_id':1})
    sentences = mongodb['veri']['translations'].find({'fileID': file[u'_id']},
                                                     {'_id': 1, 
                                                      'source_sentence': 1, 
                                                      'target_sentence': 1} ).sort('sentence_num',1)
    return sentences

def get_languages():
    languages = mongodb['veri']['translations'].find().distinct('target_language')  
    logger.info(languages)
    return languages

def get_file_names(source_language, target_language):
    file_names = mongodb['veri']['files'].find({'source_language': source_language, 
                                                'target_language': target_language},
                                               {'_id': 0,
                                                'file_path': 1})  
    logger.info(file_names)
    return file_names

def audit(action, last_editor, current_user, doc, new_target_sentence=None):
    if action is 'edit':
        mongodb['veri']['audits'].insert({'action': action,
                                          'last_editor': last_editor, 
                                          'current_user': current_user,
                                          'original_document': doc, 
                                          'new_target_sentence': new_target_sentence,
                                          'timestamp': datetime.datetime.utcnow() })
    else:
        mongodb['veri']['audits'].insert({'action': action, 
                                          'last_editor': last_editor,
                                          'current_user': current_user,
                                          'original_document': doc, 
                                          'timestamp': datetime.datetime.utcnow() })
        

class File(object):
    def __init__(self, source=None, oid=None):
        self.state = { u'file_path': None,
                       u'locked': False,
                       u'priority': 0,
                       u'source_language': None,
                       u'target_language': None}
        if source is not None:
            for k,v in source.iteritems():
                if not self.state.has_key(k):
                    logger.debug(k)
                    raise KeyError

            for k,v in source.iteritems():
                self.state[k] = v
            self.save()
        elif oid is not None:
            record = mongodb['veri']['files'].find_one({'_id':oid})
            for k,v in record.iteritems():
                self.state[k] = v
    
    def save(self):
        logger.info(self.state)
        self.state[u'_id'] = mongodb['veri']['files'].save(self.state)
 
    @property
    def file_path(self):
        return self.state[u'file_path']
     
    @property
    def priority(self):
        return self.state[u'priority']
    
    @property
    def target_language(self):
        return self.state[u'target_language']    

    @property
    def source_language(self):
        return self.state[u'source_language']    

    @property
    def _id(self):
        return self.state[u'_id']    
    
    def is_locked(self):
        return self.state[u'locked']

    def lock(self):
        if self.is_locked:
            raise Exception
        self.state[u'locked'] = True

    def unlock(self):
        self.state[u'locked'] = False

    def total_approved(self):
        return mongodb['veri']['translations'].find({'fileID':self._id, 'status': 'approved'}).count()

    def total_reviewed(self):
        return mongodb['veri']['translations'].find({'fileID':self._id, 'status': { '$in': ['reviewed', 'approved']}}).count()

    def get_total(self):
        return mongodb['veri']['translations'].find({'fileID':self._id}).count()

class Sentence(object):
    def __init__(self, source=None, oid=None):
        self.state = { u'created_at': datetime.datetime.utcnow(), 
                       u'userID': None, 
                       u'source_language': None, 
                       u'source_sentence': None, 
                       u'sentence_num': -1, 
                       u'fileID': None, 
                       u'sentenceID': None, 
                       u'target_sentence': None, 
                       u'status': u'init', 
                       u'update_number': 0, 
                       u'target_language': None,  
                       u'approvers' : [] }

        if source is not None:
            logger.debug(source)
            for k,v in source.iteritems():
                if not self.state.has_key(k):
                    logger.debug(k)
                    raise KeyError

            for k,v in source.iteritems():
                self.state[k] = v
            self.save()
        elif oid is not None:
            record = mongodb['veri']['translations'].find_one({'_id':oid})
            for k,v in record.iteritems():
                self.state[k] = v

    def edit(self, new_editor, new_target_sentence):
        audit("edit", self.userID, new_editor._id, self.state, new_target_sentence)
        self.increment_update_number()
        self.userID = new_editor._id
        self.target_sentence = new_target_sentence
        self.status = 'reviewed'
        self.num_approves = 0
        self.save()
        
 
    def approve(self, prev_editor, approver):
        if prev_editor is approver:
            logger.debug('editor is approver')
            raise Exception
        if self.userID != prev_editor._id:
            logger.debug('no match')
            raise Exception
        audit("approve", prev_editor._id, approver._id, self.state)
        self.increment_update_number()
        approver.increment_user_approved()
        self.add_approver(approver._id)
        prev_editor.increment_got_approved()
        if approver.trust_level is 'full':
            self.status = 'approved'
        prev_editor.save()
        approver.save()
        self.save()

    def unapprove(self, prev_editor, unapprover):
        if self.userID !=  prev_editor._id:
            raise Exception
        audit("unapprove", prev_editor._id, unapprover._id, self.state)
        self.increment_update_number()
        unapprover.decrement_user_approved()
        prev_editor.decrement_got_approved()
        prev_editor.save()
        unapprover.save()
        self.save()
    
    def save(self):
        logger.info(self.state)
        self.state[u'_id'] = mongodb['veri']['translations'].save(self.state)
    '''
    def archive(self):
        
        #This function archives the previous version of this sentence object
        #It finds an object in the database with the matching _id and then saves it to the archive collection
        
        record = mongodb['veri']['translations'].find_one({'_id':self.state[u'_id']},{'_id':0})
        mongodb['veri']['archive'].save(record)
    '''
    @property
    def target_language(self):
        return self.state[u'target_language']
     
    @target_language.setter
    def target_language(self, value): 
        if value in (u'es', u'jp', u'cz'): 
           self.state[u'target_language'] = value
        else: 
           raise TypeError    
    
    @property
    def source_language(self):
        return self.state[u'source_language']
    
    @source_language.setter
    def source_language(self, value): 
        if value in (u'en'): 
           self.state[u'source_language'] = value
        else: 
           raise TypeError    
    
    @property
    def userID(self):
        return self.state[u'userID']
    
    @userID.setter
    def userID(self, value):
        self.state[u'userID'] = value
    
    @property
    def status(self):
        return self.state[u'status']
    
    @status.setter
    def status(self, value): 
        if value in (u'smt', u'reviewed', u'approved'): 
           self.state[u'status'] = value
        else: 
           raise TypeError    
    
    @property
    def fileID(self):
        return self.state[u'fileID']
    
    @property
    def create_at(self):
        return self.state[u'created_at']
    
    @property
    def source_sentence(self):
        return self.state[u'source_sentence']
 
    @property
    def target_sentence(self):
        return self.state[u'target_sentence'] 
    
    @target_sentence.setter
    def target_sentence(self, value):
        self.state[u'target_sentence'] = value
    
    def increment_update_number(self):
        self.state[u'update_number'] = self.state[u'update_number'] + 1 
    '''
    def increment_num_approves(self):
        self.state[u'num_approves'] = self.state[u'num_approves'] + 1
        if self.state[u'num_approves'] >= app.config['APPROVAL_THRESHOLD']:
            self.status = "approved" 
    
    def decrement_num_approves(self):
        self.state[u'num_approves'] = self.state[u'num_approves'] - 1
        if self.state[u'num_approves'] < app.config['APPROVAL_THRESHOLD']:
            self.status = "reviewed" 
    '''
    def num_approves(self):
        return len(self.state[u'approvers'])
    
    def add_approver(self, userID):
        if userID in self.state[u'approvers']:
            raise Exception
        self.state[u'approvers'].append(userID)
        if self.num_approves() >= app.config['APPROVAL_THRESHOLD']:
            self.status = "approved" 

    def remove_approver(self, userID):
        self.state[u'approvers'].remove(userID)
        if self.num_approves() < app.config['APPROVAL_THRESHOLD']:
            self.status = "reviewed" 
    

class User(object):
    def __init__(self, source=None, oid=None, username=None):
        self.state = {u'username': username, 
                      u'num_reviewed': 0, 
                      u'num_user_approved': 0, 
                      u'num_got_approved': 0,
                      u'trust_level': 'basic' }
        
        if source is not None:
            for k,v in source.iteritems():
                if not self.state.has_key(k):
                    logger.debug(k)
                    raise KeyError

            for k,v in source.iteritems():
                self.state[k] = v
            self.save()
        elif oid is not None:
            record = mongodb['veri']['users'].find_one({'_id':oid})
            for k,v in record.iteritems():
                self.state[k] = v
        elif username is not None:
            record = mongodb['veri']['users'].find_one({'username':username})
            for k,v in record.iteritems():
                self.state[k] = v
         
    def save(self): 
        logger.info(self.state)
        self.state[u'_id'] = mongodb['veri']['users'].save(self.state) 
        # mongodb['veri']['users'].update({'username':self.state['username']}, {'$set':{'num_reviewed':self.state['num_reviewed'], 'num_user_approved':self.state['num_user_approved'], 'num_got_approved':self.state['num_got_approved']}},upsert=True)
    
    @property
    def _id(self):
        return self.state[u'_id']  
    
    @property
    def username(self):
        return self.state[u'username']  

    @property
    def num_translated(self):
        return self.state[u'num_reviewed']  
    
    @property
    def num_user_approved(self):
        return self.state[u'num_user_approved']  
    
    def increment_user_approved(self):
        self.state[u'num_user_approved'] = self.state[u'num_user_approved'] + 1
    
    def decrement_user_approved(self):
        self.state[u'num_user_approved'] = self.state[u'num_user_approved'] - 1
    
    @property
    def num_got_approved(self):
        return self.state[u'num_got_approved'] 

    def increment_got_approved(self):
        self.state[u'num_got_approved'] = self.state[u'num_got_approved'] + 1
    
    def decrement_got_approved(self):
        self.state[u'num_got_approved'] = self.state[u'num_got_approved'] - 1

    @property
    def trust_level(self):
        return self.state[u'trust_level']
     
    @trust_level.setter
    def trust_level(self, value): 
        if value in (u'basic', u'partial', u'full'): 
           self.state[u'trust_level'] = value
        else: 
           raise TypeError    
    
