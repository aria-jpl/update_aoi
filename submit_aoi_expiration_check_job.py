#!/usr/bin/env python

'''
Submits a job to check for expired AOIs & sends out a report via email
'''

import argparse
from hysds_commons.job_utils import submit_mozart_job

def main(emails, days, job_version='master', queue='facotutm-job_worker-small', priority=7):
    '''submits the job for AOI checking'''
    params = {"days": days, "emails": emails}
    job_name = 'check_aoi_expiration:{0}'.format(job_version)
    job_spec = 'job-check_aoi_expiration:{0}'.format(job_version)
    submit_job(job_name, job_spec, params, queue, priority, False)

def submit_job(job_name, job_spec, params, queue, priority, dedup):
    '''submits job through hysds wiring'''
    rule = {
        "rule_name": job_spec,
        "queue": queue,
        "priority": priority,
        "kwargs":'{}'
    }
    hysdsio = {"id": "internal-temporary-wiring", "params": params, "job-specification": job_spec}
    submit_mozart_job({}, rule, hysdsio=hysdsio, job_name=job_name, enable_dedup=dedup)

def argparser():
    '''
    Construct a parser to parse arguments
    @return argparse parser
    '''
    parse = argparse.ArgumentParser(description="Submits a check for AOI expiration")
    parse.add_argument("--emails", help="comma separated email list", required=True, dest="emails")
    parse.add_argument("--days", help="number of days to look forward", default=7, required=False, dest="days")
    parse.add_argument("--job_version", required=False, help="version of job to run, ex: master, release-20180101", dest="job_version", default="master")
    parse.add_argument("--queue", required=False, help="job queue", dest="queue", default="factotum-job_worker-small")
    parse.add_argument("--priority", required=False, help="job priority", dest="priority", default=5)
    return parse

if __name__ == '__main__':
    args = argparser().parse_args()
    main(args.emails, args.days, job_version=args.job_version, queue=args.queue, priority=args.priority)
