from cloudscheduler.job import Job

# We need to decide on logic for deciding if a job has been scheduled or not yet
# Unsure if we can rely on the metadata from the job but right now it just deaults to not scheduled

class JobManager:
    def __init__(self):

        self.unscheduled_jobs = {}
        self.unscheduled_jobs_by_user = {}
        self.scheduled_jobs = {}
        self.scheduled_jobs_by_user = {}

        self.user_list = list()


# accepts a group of job dictionaries and shuffles them into the existing dictionaries based on their
# GlobalJobIds.
    def update_jobs(self, jobs):
        for job in jobs:
            j = Job(**job)
            if j.GlobalJobId in self.unscheduled_jobs:
                #update unscheduled entry
                self.unscheduled_jobs[j.GlobalJobId] = j
                
            elif j.GlobalJobId in self.scheduled_jobs:
                #update scheduled entry
                j.set_state(1)
                self.scheduled_jobs[j.GlobalJobId] = j
                
            else:
                #brand new job, insert into unscheduled dicts
                self.unscheduled_jobs[j.GlobalJobId] = j
                self.unscheduled_jobs_by_user[j.User][j.GlobalJobId] = j

    def schedule_job(self, jobid):
        self.unscheduled_jobs[jobid].set_state(1)
        job = self.unscheduled_jobs[jobid]
        self.scheduled_jobs[jobid] = job
        self.scheduled_jobs_by_user[job.User][jobid] = job
        del self.unscheduled_jobs[jobid]
        del self.unscheduled_jobs_by_user[job.User][jobid]
        

    def unschedule_job(self, jobid):
        self.scheduled_jobs[jobid].set_state(0)
        job = self.scheduled_jobs[jobid]
        self.unscheduled_jobs[jobid] = job
        self.unscheduled_jobs_by_user[job.User][jobid] = job
        del self.scheduled_jobs[jobid]
        del self.scheduled_jobs_by_user[job.User][jobid]

    def get_jobs_user(self, user):
        unsched = self.unscheduled_jobs_by_user[user]
        sched = self.scheduled_jobs_by_user[user]
        #python 3 expression for merging 2 dicts, for 2 you need to copy each dict
        user_jobs = {**unsched, **sched}
        return user_jobs

    def get_scheduled_jobs_user(self, user):
        return self.scheduled_jobs_by_user[user]

    def get_unscheduled_jobs_user(self, user):
        return self.unscheduled_jobs_by_user[user]

    def get_unscheduled_jobs(self):
        return self.unscheduled_jobs

    def get_scheduled_jobs(self):
        return self.scheduled_jobs

    def get_all_jobs(self):
        unsched = self.unscheduled_jobs
        sched = self.scheduled_jobs
        #python 3 expression for merging 2 dicts, for 2 you need to copy each dict
        all_jobs = {**unsched, **sched}
        return all_jobs

    def update_users(self):
        self.user_list = list(set(self.unscheduled_jobs_by_user.keys()) + set(self.scheduled_jobs_by_user.keys()))

    def get_users(self):
        return self.user_list
