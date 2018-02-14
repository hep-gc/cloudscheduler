"""
Old JobManager / container module. Likely to go away since using database for jobs.
"""

from cloudscheduler.job import Job

# We need to decide on logic for deciding if a job has been scheduled or not yet
# Unsure if we can rely on the metadata from the job but right now it just defaults to not scheduled

class JobManager:

    """
    Job Manager Class to assist with scheduling jobs.
    """
    def __init__(self):
        """
        Init for job manager.
        """

        self.unscheduled_jobs = {}
        self.unscheduled_jobs_by_user = {}
        self.scheduled_jobs = {}
        self.scheduled_jobs_by_user = {}

        self.user_list = list()


    # accepts a group of job dictionaries and shuffles them into the existing
    #  dictionaries based on their globaljobids.
    def update_jobs(self, jobs):
        """
        update job states.
        :param jobs: list of jobs from condor?
        """
        redis_key_list = []
        for job in jobs:
            j = Job(**job)
            redis_key_list.append(j.globaljobid)
            if j.globaljobid in self.unscheduled_jobs:
                #update unscheduled entry
                self.unscheduled_jobs[j.globaljobid] = j
                self.unscheduled_jobs_by_user[j.user][j.globaljobid] = j

            elif j.globaljobid in self.scheduled_jobs:
                #update scheduled entry
                j.set_state(1)
                self.scheduled_jobs[j.globaljobid] = j
                self.scheduled_jobs_by_user[j.user][j.globaljobid] = j

            else:
                #brand new job, insert into unscheduled dicts
                self.unscheduled_jobs[j.globaljobid] = j
                self.unscheduled_jobs_by_user[j.user][j.globaljobid] = j
        # Clean up jobs that were not in the redis store
        for key in self.scheduled_jobs:
            if key not in redis_key_list:
                del self.scheduled_jobs[key]
                del self.scheduled_jobs_by_user[key]
        for key in self.unscheduled_jobs:
            if key not in redis_key_list:
                del self.unscheduled_jobs[key]
                del self.unscheduled_jobs_by_user[key]


    def schedule_job(self, jobid):
        """
        Mark a job as scheduled.
        :param jobid: id of job to mark
        """
        self.unscheduled_jobs[jobid].set_state(1)
        job = self.unscheduled_jobs[jobid]
        self.scheduled_jobs[jobid] = job
        self.scheduled_jobs_by_user[job.user][jobid] = job
        del self.unscheduled_jobs[jobid]
        del self.unscheduled_jobs_by_user[job.user][jobid]


    def unschedule_job(self, jobid):
        """
        Unmark a previously scheduled job.
        :param jobid: id of job to unmark
        """
        self.scheduled_jobs[jobid].set_state(0)
        job = self.scheduled_jobs[jobid]
        self.unscheduled_jobs[jobid] = job
        self.unscheduled_jobs_by_user[job.user][jobid] = job
        del self.scheduled_jobs[jobid]
        del self.scheduled_jobs_by_user[job.user][jobid]

    def get_jobs_user(self, user):
        """
        Fetch the jobs for specified user.
        :param user: user to get jobs for.
        :return: list of jobs belonging to user or None.
        """
        unsched = self.unscheduled_jobs_by_user[user]
        sched = self.scheduled_jobs_by_user[user]
        # python 3 expression for merging 2 dicts
        user_jobs = {**unsched, **sched}
        return user_jobs

    def get_scheduled_jobs_user(self, user):
        """
        Get the scheduled jobs for user.
        :param user: user name
        :return: job dict
        """
        return self.scheduled_jobs_by_user[user]

    def get_unscheduled_jobs_user(self, user):
        """
        Get the unscheduled jobs for a specific user.
        :param user: user name to get jobs for.
        :return: job dict
        """
        return self.unscheduled_jobs_by_user[user]

    def get_unscheduled_jobs(self):
        """
        Get the unscheduled jobs.
        :return:
        """
        return self.unscheduled_jobs

    def get_scheduled_jobs(self):
        """
        Get the scheduled jobs dictionary.
        :return:
        """
        return self.scheduled_jobs

    def get_all_jobs(self):
        """
        Return a dict containing all the jobs in system.
        :return: dict of jobs.
        """
        unsched = self.unscheduled_jobs
        sched = self.scheduled_jobs
        #python 3 expression for merging 2 dicts
        all_jobs = {**unsched, **sched}
        return all_jobs

    def update_users(self):
        """
        Update the user list with current users.
        """
        self.user_list = list(set(self.unscheduled_jobs_by_user.keys())
                              .union
                              (set(self.scheduled_jobs_by_user.keys())))

    def get_users(self):
        """
        Get a list of users in the system.
        :return: list of user names.
        """
        return self.user_list
