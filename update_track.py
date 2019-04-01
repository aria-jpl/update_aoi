#!/usr/bin/env python

'''
Update/Change track number for a given AOI
'''

import json
import requests
from hysds.celery import app

def main():
    '''main loop that updates/clears the AOI metadata with track'''
    context = load_context()
    aoi_name = context['aoi_name']
    index = context['aoi_index']
    aoi_type = context['aoi_type']
    action = context['action']
    if action == 'append':
        track_number = int(context['track_number'])
        print('appending track {} to AOI: {}'.format(track_number, aoi_name))
        append_track_num(track_number, aoi_name, index, aoi_type)
    elif action == 'clear':
        print('clearing track info for AOI: {}'.format(aoi_name))
        clear_track_num(aoi_name, index, aoi_type)
    else:
        raise Exception('invalid action type: {}'.format(action))

def append_track_num(track_number, aoi_name, index, aoi_type):
    '''update the aoi with the track number'''
    #build the track list by getting the current track and updating the new track num
    track_list = get_current_tracks(aoi_name, index, aoi_type)
    print('current tracks for {}: {}'.format(aoi_name, track_list))
    track_list.append(track_number)
    track_list = list(set(track_list)) #remove repeates
    print('updated track list: {}'.format(track_list))
    grq_ip = app.conf['GRQ_ES_URL'].rstrip(':9200').replace('http://', 'https://')
    grq_url = '{0}/es/{1}/{2}/{3}/_update'.format(grq_ip, index, aoi_type, aoi_name)
    es_query = {"doc" : {"metadata": {"track_number" : track_list}}}
    print('querying {} with {}'.format(grq_url, es_query))
    response = requests.post(grq_url, data=json.dumps(es_query), timeout=60, verify=False)
    response.raise_for_status()
    print('successfully updated track')

def get_current_tracks(aoi_name, index, aoi_type):
    '''returns the current tracks as a list, returns an empty list if none exist'''
    grq_ip = app.conf['GRQ_ES_URL'].replace(':9200', '').replace('http://', 'https://')
    grq_url = '{0}/es/{1}/{2}/{3}?fields=metadata.track_number'.format(grq_ip, index, aoi_type, aoi_name)
    print('grq url: {}'.format(grq_url))
    response = requests.get(grq_url, timeout=60, verify=False)
    response.raise_for_status()
    resp_dict = json.loads(response.text)
    if 'fields' in resp_dict.keys() and 'metadata.track_number' in resp_dict['fields'].keys():
        return resp_dict['fields']['metadata.track_number']
    return []

def clear_track_num(aoi_name, index, aoi_type):
    '''clears all track numbers from the aoi'''
    track_list = []
    grq_ip = app.conf['GRQ_ES_URL'].replace(':9200', '').replace('http://', 'https://')
    grq_url = '{0}/es/{1}/{2}/{3}/_update'.format(grq_ip, index, aoi_type, aoi_name)
    es_query = {"doc" : {"metadata": {"track_number" : track_list}}}
    print('querying {} with {}'.format(grq_url, es_query))
    response = requests.post(grq_url, data=json.dumps(es_query), timeout=60, verify=False)
    response.raise_for_status()
    print('successfully updated track')

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
