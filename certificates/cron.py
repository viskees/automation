from django_cron import CronJobBase, Schedule

class CronJobTest(CronJobBase):
    RUN_EVERY_MINS = 120 # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'certificates.cron_test'    # a unique code

    def do(self):
        pass    # do your thing here


def cron_test():
    print("cron is working!!")