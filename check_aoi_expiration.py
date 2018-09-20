#!/usr/bin/env python

'''
Checks for AOI expiration within a given time, and sends an email with the results
'''

from __future__ import print_function
import json
import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import requests
import dateutil.parser
from hysds.celery import app
from hysds_commons.net_utils import get_container_host_ip



def main():
    '''main loop that updates/clears the AOI metadata with the time'''
    ctx = load_context()
    try:
        days = float(ctx['days'])
    except:
        raise Exception('Invalid input days: "{}"'.format(ctx['days']))
    try:
        email_list = ctx['emails'].replace(' ', '').split(',')
    except:
        raise Exception('Invalid input email string: "{}"'.format(ctx['emails']))
    now = datetime.datetime.utcnow()
    now_time = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    expire = (now + datetime.timedelta(days=days))
    expire_time = expire.strftime('%Y-%m-%dT%H:%M:%SZ')
    # handle negative ranges
    if now > expire:
        now_time, expire_time = expire_time, now_time
    print('checking for AOI\'s expiring before {}'.format(expire_time))
    expiring_aois = get_expiring_aois(now_time, expire_time)
    report = build_email_report(expiring_aois, days)
    email_report(report, email_list)

def get_expiring_aois(now_time, expire_time):
    '''return the names of AOIs expiring within the given time'''
    data = '{"query":{"bool":{"must":[{"term":{"dataset_type.raw":"area_of_interest"}},{"range":{"endtime":{"gt":"%s","lt":"%s"}}}],"must_not":[],"should":[]}},"from":0,"size":5000,"sort":[{"endtime":{"order":"asc"}}],"aggs":{}}' % (now_time, expire_time)
    grq_ip = app.conf['GRQ_ES_URL'].rstrip(':9200').replace('http://', 'https://')
    grq_url = '{0}/es/_search'.format(grq_ip)
    response = requests.post(grq_url, data=data, timeout=60, verify=False)
    response.raise_for_status()
    results = json.loads(response.text)['hits']['hits']
    return results

def build_email_report(expiring_aois, days):
    '''builds the email report for all expiring AOIs'''
    aoi_report = 'Found {0} AOI\'s expiring within the next {1:.1f} days.\n\n'.format(len(expiring_aois), days)
    aoi_report += 'Current time: {}\n\n'.format(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    for aoi in expiring_aois:
        aoi_report += build_aoi_report(aoi)
    return aoi_report

def email_report(report, email_list):
    '''emails the AOI report list to the emails on the email list'''
    report_title = 'AOI Expiration Report for {}'.format(datetime.datetime.utcnow().strftime('%Y-%m-%d'))
    send_email(email_list, report_title, report)

def send_email(send_to, subject, body):
    '''send email with given inputs'''
    send_to = [str(email) for email in send_to]
    msg = MIMEText(body)
    send_to_str = ', '.join(send_to)
    sender = 'aria-ops@jpl.nasa.gov'
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = send_to_str
    print('Sending email.\nFrom: {0}\nTo: {1}\nSubject:: {2}\nBody: {3}'.format(sender, send_to, subject, body))
    smtp_obj = smtplib.SMTP(get_container_host_ip())
    smtp_obj.sendmail(sender, send_to, msg.as_string())
    smtp_obj.quit()

def build_aoi_report(aoi):
    '''builds the report for a single aoi'''
    name = aoi['_id']
    starttime_str = aoi['_source']['starttime']
    endtime_str = aoi['_source']['endtime']
    endtime = dateutil.parser.parse(endtime_str).replace(tzinfo=pytz.utc)
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    days_until_expire = float((endtime - now).total_seconds()) / 86400.0
    report = '{0}\n------------------------------\nExpires in: {1:.1f} days\nStart time: {2}\nEnd time: {3}\n\n'.format(name, days_until_expire, starttime_str, endtime_str)
    return report

def load_context():
    '''loads the context file into a dict'''
    try:
        context_file = '_context.json'
        with open(context_file, 'r') as fin:
            context = json.load(fin)
        return context
    except:
        raise Exception('unable to parse _context.json from work directory')

if __name__ == '__main__':
    main()
