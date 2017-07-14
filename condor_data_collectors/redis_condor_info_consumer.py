import htcondor
import redis
import time
import json
import classad

def setup_redis_connection():
    r = redis.StrictRedis(host="htcs-master.heprc.uvic.ca", port=6379, db=0, password=~NEED THE PW HERE~)
    return r


def import_condor_info():

    try:
        redis_con = setup_redis_connection()
        condor_resources = redis_con.get("condor-resources")
        condor_jobs = redis_con.get("condor-jobs")

        condor_resources = json.loads(condor_resources)
        condor_jobs = json.loads(condor_jobs)
        for job in condor_jobs:
            # expression trees must be cast as a string to make them json serializable
            # we must rebuild the tree from the string on this side.
            req_etree = classad.ExprTree(str(job["Requirements"]))
            job["Requirements"] = req_etree
        return condor_resources, condor_jobs

    except Exception as e:
        print(e)
        print("Exiting due to exception")
        return None


#MAIN EXECUTION

while True:
    print("Collecting condor info...")
    resource, jobs = import_condor_info()
    if resource or jobs is None:
        print("Could not retrieve job or resource data...")
    print("Sleeping for 30s...")
    time.sleep(30)

