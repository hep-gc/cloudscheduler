from cloudscheduler.job import Job

class JobManager:
    def __init__(self):
        self.jobs = {}

    def update_jobs(self, jobs):
        for job in jobs:
            j = Job(**job)
            self.jobs[j.GlobalJobId] = j

    def schedule_job(self, jobid):
        pass

    def unschedule_job(self, jobid):
        pass

    def get_jobs_user(self, user):
        pass

    def get_scheduled_jobs_user(self, user):
        pass

    def get_unscheduled_jobs_user(self, user):
        pass

    def get_users(self):
        pass

    def get_unscheduled_jobs(self):
        pass
