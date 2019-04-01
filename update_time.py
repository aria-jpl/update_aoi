#!/usr/bin/env python

'''
Update start/event/endtime field for a given AOI
'''

import json
import requests
import dateutil.parser
from hysds.celery import app

def main():
    '''main loop that updates/clears the AOI metadata with the time'''
    context = load_context()
    aoi_name = context['aoi_name']
    index = context['aoi_index']
    aoi_type = context['aoi_type']
    time_field = context['time_field']
    time_obj = dateutil.parser.parse(context['time'])
    time_string = time_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    print('updating {} {} to: {}'.format(aoi_name, time_field, time_string))
    update_time(index, aoi_type, aoi_name, time_field, time_string)

def update_time(index, aoi_type, aoi_name, time_field, time):
    '''update the aoi with the correct time field'''
    #build the track list by getting the current track and updating the new track num
    grq_ip = app.conf['GRQ_ES_URL'].rstrip(':9200').replace('http://', 'https://')
    grq_url = '{0}/es/{1}/{2}/{3}/_update'.format(grq_ip, index, aoi_type, aoi_name)
    if time_field == 'eventtime':
        es_query = {"doc" : {"metadata": {time_field : time}}}
    else:
        es_query = {"doc" : {time_field: time}}
    print('querying {} with {}'.format(grq_url, es_query))
    response = requests.post(grq_url, data=json.dumps(es_query), timeout=60, verify=False)
    response.raise_for_status()
    print('successfully updated time.')

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
