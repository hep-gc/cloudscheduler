from cloudscheduler.job import Job

class JobManager:
    def __init__(self):
        self.jobs = {}
        self.jobs_by_user = {}
        self.scheduled_jobs = {}
        self.scheduled_jobs_by_user = {}


        self.user_list = list()

    def update_jobs(self, jobs):
        for job in jobs:
            j = Job(**job)
            self.jobs[j.GlobalJobId] = j
            self.jobs_by_user[j.User][j.GlobalJobId] = j

    def schedule_job(self, jobid):
        self.jobs[jobid].set_state(1)
        job = self.jobs[jobid]
        self.scheduled_jobs[jobid] = job
        self.scheduled_jobs_by_user[job.User][jobid] = job
        

    def unschedule_job(self, jobid):
        self.jobs[jobid].set_state(0)
        job = self.jobs[jobid]
        del self.scheduled_jobs[jobid]
        del self.scheduled_jobs_by_user[job.User][jobid]

    def get_jobs_user(self, user):
        return self.jobs_by_user[user]

    def get_scheduled_jobs_user(self, user):
        return self.scheduled_jobs_by_user[user]

    def get_unscheduled_jobs_user(self, user):
        pass


    def get_unscheduled_jobs(self):
        pass

    def update_users(self, user_list):
        pass

    def get_users(self):
        pass