import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import csjobs

class TestCSJobsMethods(unittest.TestCase):

    def setUp(self):
        r = csjobs.setup_redis_connection()
        r.flushall()

    def test_valid_command(self):
        r = csjobs.setup_redis_connection()
        r.rpush("job_commands", '{"job_id": "2479.19", "command": "set_job_hold"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertTrue(csjobs.job_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("job_commands"))


    def test_invalid_command(self):
        r = csjobs.setup_redis_connection()
        r.rpush("job_commands", '{"machine_name": "2479.21", "command": "condor_FAKE_COMMAND"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(csjobs.job_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("job_commands"))


    def test_invalid_job_id(self):
        r = csjobs.setup_redis_connection()
        r.rpush("job_commands", '{"job_id": "s4D5F6G7H8J9asdf!@#$%&*()", "command": "set_job_hold"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(csjobs.job_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("job_commands"))


    def test_no_command(self):
        r = csjobs.setup_redis_connection()
        r.rpush("job_commands", '{"job_id": "2479.19"')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(csjobs.job_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("job_commands"))

    def test_no_job_id(self):
        r = csjobs.setup_redis_connection()
        r.rpush("job_commands", '{"command": "set_job_hold"}')
        
        #will return true if a condor command is run, false otherwise.
        self.assertFalse(csjobs.job_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        r = csjobs.setup_redis_connection()
        self.assertIsNone(r.lpop("job_commands"))


    def test_empty_queue(self):
        self.assertFalse(csjobs.job_command_consumer(testrun=True))

        #Double check to make sure the queue was emptied
        self.assertIsNone(r.lpop("job_commands"))



# BEGIN DATA PRODUCER TESTS
    def test_data_dump(self):
        self.assertTrue(csjobs.resources_producer(testrun=True, testfile="/opt/cloudscheduler/condor_data_collectors/tests/test_job_list.txt"))
        r = csjobs.setup_redis_connection()
        


    def test_no_condor_data_dump(self):
        self.assertTrue(csjobs.resource_producer(testrun=True, testfile="/opt/cloudscheduler/condor_data_collectors/tests/empty_condor_data.txt"))
        r = csjobs.setup_redis_connection()

        redis_jobs = r.get("condor-jobs")
        redis_jobs = json.loads(redis_rjobs)
        job_file = open("/opt/cloudscheduler/condor_data_collectors/tests/test_condor_jobs.txt", 'r')
        condor_jobs = job_file.read()[0:-1] #strip newline
        condor_jobs = json.loads(condor_jobs)
        self.assertEqual(redis_jobs, condor_jobs)

