import redis
import json
#import config

def setup_redis_connection():
    #r = redis.StrictRedis(host=config.redis_host, port=config.redis_port, db=config.redis_db, password=config.redis_password)
    r = redis.StrictRedis(host="htcs-master.heprc.uvic.ca", port=6379, db=0, password=NEEDAPWHERE~~)
    return r

def send_hold_job(job_id):
    #job_command_key = config.job_commands_key
    r = setup_redis_connection()
    cmd_dict = {
                 "command": "set_job_hold",
                 "job_id": job_id
               }
    cmd_string = json.dumps(cmd_dict)
    try:
    	r.lpush("job_commands", cmd_string)
    	return True
    except:
    	print("Error sending command to redis...")
    	return False


def send_condor_off(machine_name):
	#collector_command_key = config.collector_commands_key
	r = setup_redis_connection()
    cmd_dict = {
                 "command": "condor_off",
                 "machine_name": machine_name
               }
    cmd_string = json.dumps(cmd_dict)
    try:
    	r.lpush("collector_commands", cmd_string)
    	return True
    except:
    	print("Error sending command to redis...")
    	return False

if __name__ == '__main__':
    #main execution
    #todo
