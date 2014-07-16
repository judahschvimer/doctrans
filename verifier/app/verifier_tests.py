import time
import atexit
import shutil
import tempfile
import unittest
import subprocess
import my_util
import pymongo
import os
import logging
import models

MONGODB_TEST_PORT = 31415
PATH_TO_MONGOD = '/home/wisdom/mongodb/2.6.0-rc0'
DBNAME = 'veritest'

logger = logging.getLogger('tests')
logging.basicConfig(level=logging.DEBUG)

class MongoTemporaryInstance(object):
    '''Singleton to manage a temporary MongoDB instance

    Use this for testing purpose only. The instance is automatically destroyed
    at the end of the program.
    Courtesy of: http://blogs.skicelab.com/maurizio/python-unit-testing-and-mongodb.html
    '''
    _instance = None

    @classmethod
    def get_instance(cls):
        '''This method gets an instance that's destroyed at the end of the program'''
        if cls._instance is None:
            cls._instance = cls()
            atexit.register(cls._instance.shutdown)
        return cls._instance

    def __init__(self):
        self._tmpdir = tempfile.mkdtemp()
        logger.info(self._tmpdir)
        self._process = subprocess.Popen('{0}/mongod --bind_ip localhost --port {1} --dbpath {2} --nojournal --nohttpinterface --noauth --smallfiles --syncdelay 0 --maxConns 10 --nssize 1'.format(PATH_TO_MONGOD, MONGODB_TEST_PORT, self._tmpdir), shell=True, executable='/bin/bash')
        #      wait for the instance to be ready
        #      Mongo is ready in a glance, we just wait to be able to open a
        #      Connection.

        for i in range(3):
            time.sleep(1)
            try:
                self._client = pymongo.MongoClient('localhost', MONGODB_TEST_PORT)
            except pymongo.errors.ConnectionFailure:
                continue
            else:
                break
        else:
            self.shutdown()
            assert False, 'Cannot connect to the mongodb test instance'

    @property
    def client(self):
        return self._client

    def shutdown(self):
        '''This method destroys the process and the instance'''
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
            shutil.rmtree(self._tmpdir, ignore_errors=True)


class TestCase(unittest.TestCase):
    '''TestCase with an embedded MongoDB temporary instance.

    Each test runs on a temporary instance of MongoDB. Please note that
    these tests are not thread-safe and different processes should set a
    different value for the listening port of the MongoDB instance with the
    settings `MONGODB_TEST_PORT`.

    A test can access the connection using the attribute `conn`.

    '''
    db_init_files = ['test_files/translations.json','test_files/users.json']
    
    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.db_inst = MongoTemporaryInstance.get_instance()
        self.client = self.db_inst.client
        self.db = self.client[DBNAME]

    def sentence(self, id=None):
        s = models.Sentence(oid=id, curr_db=self.db)
        return s
    
    def user(self, id=None):
        u = models.User(oid=id, curr_db=self.db)
        return u
    
    def file(self, id=None):
        f = models.File(oid=id, curr_db=self.db)
        return f
    
    def setUp(self):
        '''This method sets up the test by deleting all of the tables in the database and reloading it'''
        super(TestCase, self).setUp()

        for db_name in self.client.database_names():
            self.client.drop_database(db_name)

        for f in self.db_init_files:
            my_util.load_json(f,self.db)

    def test_setup(self):
        '''This test tests that the database sets up properly''' 
        pass

    def test_edit(self):
        '''This test tests a simple edit works as it should'''
        logger.debug(self.db)
        logger.debug(self.db.translations.find_one({'_id':u's1'}))
        s = self.sentence(id=u's1')
        s_old = self.sentence(id=u's1')
        moses = self.user(id=u'u1')
        judah = self.user(id=u'u2')
        judah_old = self.user(id=u'u2')
        s.edit(judah, u'foo bar') 
        s = self.sentence(id=u's1')
        judah = self.user(id=u'u2')
        self.assertEquals(s.update_number, 1)
        self.assertEquals(s.target_sentence,u'foo bar')
        self.assertEquals(s.userID,judah._id)
        self.assertEquals(s.source_sentence, s_old.source_sentence)
        self.assertEquals(s.sentenceID, s_old.sentenceID)
        self.assertEquals(s.sentence_num, s_old.sentence_num)
        self.assertEquals(s.source_language, s_old.source_language)
        self.assertEquals(s.target_language, s_old.target_language) 
        self.assertEquals(s.status, u'reviewed')
        self.assertEquals(s.approvers, [])

        self.assertEquals(judah.username, judah_old.username)
        self.assertEquals(judah.num_got_approved, judah_old.num_got_approved)
        self.assertEquals(judah.num_user_approved, judah_old.num_user_approved) 
        self.assertEquals(judah.trust_level, judah_old.trust_level)
        self.assertEquals(judah.num_reviewed, 1)

    def test_approve(self):
        '''This method tests that the approve command works properly'''
        s = self.sentence(id=u's1')
        s_old = self.sentence(id=u's1')
        judah = self.user(id=u'u2')
        judah_old = self.user(id=u'u2')
        s.approve(judah) 
        s = self.sentence(id=u's1')
        judah = self.user(id=u'u2')
        moses = self.user(id=u'u1')
        self.assertEquals(s.update_number, 1)
        self.assertEquals(s.target_sentence, s_old.target_sentence)
        self.assertEquals(s.userID, s_old.target_sentence)
        self.assertEquals(s.source_sentence, s_old.source_sentence)
        self.assertEquals(s.sentenceID, s_old.sentenceID)
        self.assertEquals(s.sentence_num, s_old.sentence_num)
        self.assertEquals(s.source_language, s_old.source_language) 
        self.assertEquals(s.target_language, s_old.target_language) 
        self.assertEquals(s.status, u'reviewed')
        self.assertEquals(s.approvers, [u'u2'])

        self.assertEquals(judah.username, judah_old.username)
        self.assertEquals(judah.num_got_approved, judah_old.num_got_approved) 
        self.assertEquals(judah.num_user_approved, judah_old.num_user_approved + 1)  
        self.assertEquals(judah.trust_level, judah_old.trust_level) 
        self.assertEquals(judah.num_reviewed, 1)
       

if __name__ == '__main__':
    unittest.main()