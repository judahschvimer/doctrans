import datetime
from pymongo import MongoClient
import logging
from .  import app

logger = logging.getLogger('models')
logging.basicConfig(level=logging.DEBUG)

mongodb = MongoClient('localhost', 28000)
db = mongodb[app.config['MONGO_DBNAME']]

def get_sentences_in_file(fp, source_language, target_language):
    '''This function  gets all of the sentences in the given file 
    :Parameters:
        - 'fp': path to the file
        - 'source_language': source language
        - 'target_language': target language
    :Returns:
        - cursor of sentences
    '''
    logger.debug(fp)
    file = db['files'].find_one({'source_language': source_language, 
                                              'target_language': target_language, 
                                              'file_path': fp}, 
                                             {'_id':1})
    sentences = db['translations'].find({'fileID': file[u'_id']},
                                                     {'_id': 1, 
                                                      'source_sentence': 1, 
                                                      'target_sentence': 1,
                                                      'approvers':1,
                                                      'userID':1} ).sort('sentence_num',1)
    return sentences

def get_languages():
    '''This function gets all of the unique target languages 
    :Returns:
        - cursor of languages
    '''
    languages = db['translations'].find().distinct('target_language')  
    logger.info(languages)
    return languages

def get_file_names(source_language, target_language):
    '''This function  gets all of the file names for a given pair of languages 
    :Parameters:
        - 'source_language': source language
        - 'target_language': target language
    :Returns:
        - cursor of file names
    '''
    file_names = db['files'].find({'source_language': source_language, 
                                                'target_language': target_language},
                                               {'_id': 0,
                                                'file_path': 1})  
    logger.info(file_names)
    return file_names

def audit(action, last_editor, current_user, doc, new_target_sentence=None):
    ''' This function saves an audit of the event that occurred 
    :Parameters:
        - 'action': edit, approve, or unapprove
        - 'last editor': last person to edit the sentence before this action occurred
        - 'current user': user who did the action 
        - 'doc': original python dictionary of old data
        - 'new_target_sentence': new translation of the sentence, might be none if action is approved 
    '''
    if action is 'edit':
        db['audits'].insert({'action': action,
                                          'last_editor': last_editor, 
                                          'current_user': current_user,
                                          'original_document': doc, 
                                          'new_target_sentence': new_target_sentence,
                                          'timestamp': datetime.datetime.utcnow() })
    else:
        db['audits'].insert({'action': action, 
                                          'last_editor': last_editor,
                                          'current_user': current_user,
                                          'original_document': doc, 
                                          'timestamp': datetime.datetime.utcnow() })
        

class File(object):
    '''This class models a file.
    It has a lock on it so no two people can edit the file at the same time. It has a priority to say how important translation it is
    It also has a set of languages 
    '''
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
    ''' This class models a sentence.
    A sentence has a user who last edited it, a pair of languages and sentences in those languages, a file and a sentence number in that file.
    It also has a status, and update number, and approvers
    '''
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
        '''This function edits the current sentence.
        :Parameters:
            - 'new_editor': The userID of the person who just edited it
            - 'new_target_sentence': new translation of the sentence
        '''
        if self.check_approver(new_editor._id):
            logger.error("editor already approved")
            raise Exception
        audit("edit", self.userID, new_editor._id, self.state, new_target_sentence)
        self.increment_update_number()
        self.userID = new_editor._id
        self.target_sentence = new_target_sentence
        self.status = 'reviewed'
        self.state['approvers'] = []
        self.save()
        
 
    def approve(self, prev_editor, approver):
        '''This function approves the current sentence.
        :Parameters:
            - 'prev_editor': The userID of the person who last edited it
            - 'approver': The userID of the person who just approved it
        '''
        if prev_editor._id == approver._id:
            logger.error('cannot approve own edit')
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
        '''This function unapproves the current sentence.
        :Parameters:
            - 'prev_editor': The userID of the person who last edited it
            - 'unapprover': The userID of the person who just unapproved it
        '''
        if self.check_approver(unapprover._id) is False:
            logger.error("never approved sentence")
            raise exception
        if self.userID !=  prev_editor._id:
            logger.debug('no match')
            raise Exception
        audit("unapprove", prev_editor._id, unapprover._id, self.state)
        self.increment_update_number()
        self.remove_approver(unapprover._id)
        unapprover.decrement_user_approved()
        prev_editor.decrement_got_approved()
        prev_editor.save()
        unapprover.save()
        self.save()
    
    def save(self):
        logger.info(self.state)
        self.state[u'_id'] = mongodb['veri']['translations'].save(self.state)
  
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
   
    def check_approver(self, userID):
        return userID in self.state[u'approvers'] 

class User(object):
    ''' This class models a user.
    A user has a username, a number of reviews, and number of sentences that the user approved and anumber of sentences that the user edited that were approved
    A user also has a trust level specifying how much trust we put in them for their translations and approvals
    '''
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
    
