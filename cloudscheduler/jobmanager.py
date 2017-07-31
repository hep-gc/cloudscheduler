from cloudscheduler.job import Job

class JobManager:
    def __init__(self):
        self.jobs = {}

    def update_jobs(self, jobs):
        for job in jobs:
            j = Job(**job)
            self.jobs[j.GlobalJobId] = j

