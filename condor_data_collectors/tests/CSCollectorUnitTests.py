import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import unittest
import cscollector

valid_machine_name = "slot1_1@beaver-efb4c32d-4cac-4928-9146-37dbaf30b452.novalocal"
cloud_sched_root_dir ="/opt/cloudscheduler/"

## THESE TESTS SHOULD BE UPGRADED TO USE THE CONFIG VALUES INSTEAD OF HARD-CODING REDIS KEYS

class TestCSCollectorMethods(unittest.TestCase):

    def setUp(self):
        r = cscollector.setup_redis_connection()
        r.flushall()

# BEGIN COMMAND CONSUMER TESTS

    def test_valid_command(self):
        r = cscollector.setup_redis_connection()
        r.rpush("collector_commands", '{"machine_name": "' + valid_machine_name + '", "command": "condor_off"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertTrue(cscollector.collector_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("collector_commands"))


    def test_invalid_command(self):
        r = cscollector.setup_redis_connection()
        r.rpush("collector_commands", '{"machine_name": "' + valid_machine_name + '", "command": "condor_FAKE_COMMAND"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(cscollector.collector_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("collector_commands"))


    def test_invalid_machine_name(self):
        r = cscollector.setup_redis_connection()
        r.rpush("collector_commands", '{"machine_name": "GARBAGEMACHINE", "command": "condor_off"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(cscollector.collector_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("collector_commands"))


    def test_no_command(self):
        r = cscollector.setup_redis_connection()
        r.rpush("collector_commands", '{"machine_name": "GARBAGEMACHINE"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(cscollector.collector_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("collector_commands"))


    def test_no_machine_name(self):
    	r = cscollector.setup_redis_connection()
    	r.rpush("collector_commands", '{"command": "condor_off"}')
    	
    	#will return true if a condor command is run, false otherwise.
        self.assertFalse(cscollector.collector_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("collector_commands"))


    def test_empty_queue(self):
    	#will return true if a condor command is run, false otherwise.
        self.assertFalse(cscollector.collector_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        r = cscollector.setup_redis_connection()
        self.assertIsNone(r.lpop("collector_commands"))



# BEGIN DATA PRODUCER TESTS
    def test_no_data_dump(self):
    	self.assertFalse(cscollector.resources_producer(testrun=True))
    	
    	r = cscollector.setup_redis_connection()
    	redis_resources = r.get("condor-resources")

    	self.assertEqual(redis_resources, None)


    def test_data_dump(self):
    	self.assertTrue(cscollector.resources_producer(testrun=True, testfile=cloud_sched_root_dir + "condor_data_collectors/tests/test_condor_resources.txt"))
    	r = cscollector.setup_redis_connection()

    	redis_resources = r.get("condor-resources")
        redis_resources = json.loads(redis_resources)
    	res_file = open(cloud_sched_root_dir + "condor_data_collectors/tests/test_condor_resources.txt", 'r')
        condor_resources = res_file.read()[0:-1] #strip newline
        condor_resources = json.loads(condor_resources)
        self.assertEqual(redis_resources, condor_resources)





if __name__ == '__main__':
    unittest.main()
