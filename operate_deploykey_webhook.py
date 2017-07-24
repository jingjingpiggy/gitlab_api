#!/usr/bin/env python
import requests
import json
import copy
import sys
import argparse

def post(url, data, headers):
    return requests.post(url, data=json.dumps(data), headers=headers).json()

def get(url, headers, payload=None):
    if payload:
        return requests.get(url, params=payload, headers=headers).json()
    return requests.get(url, headers=headers).json()

def put(url, data, headers):
    return requests.put(url, data=json.dumps(data), headers=headers).json()

def delete(url, headers):
    return requests.delete(url, headers=headers).json()



class Project(object):


    def __init__(self, name, url, token):

        def get_project_id(name):
            '''Get id of project'''
            self.payload['search'] = name
            url = self.url + 'api/v3/projects'
            project_info = get(url, self.headers, self.payload)

            if not project_info:
                print "%s project isn't in gitlab" % name
                return 0
            try:
                return get(url, self.headers, self.payload)[0]['id']
            except KeyError:
                print get(url, self.headers, self.payload)


        self.url = url
        self.headers = {'PRIVATE-TOKEN': token}
        self.payload = {}
        self.project_id = get_project_id(name)

    def list_webhooks(self):
        '''List all webhooks of a project'''
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/hooks'
        return get(url, self.headers)

    def get_webhook(self, webhook_id):
        '''Get webhook'''
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/hooks/' + str(webhook_id)
        return get(url, self.headers)

    def post_webhook(self, data):
        '''Add webhook'''
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/hooks'
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/json"
        return post(url, data, headers)

    def put_webhook(self, webhook_id, data):
        '''Edit webhook'''
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/hooks/' + str(webhook_id)
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/json"
        return put(url, data, headers)

    def del_webhook(self, webhook_id):
        '''Delete webhook'''
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/hooks/' + str(webhook_id)
        return delete(url, self.headers)

    #'--------------deploy key--------------'

    def list_deploykeys(self):
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/deploy_keys'
        return get(url, self.headers)

    def post_deploykey(self, data):
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/deploy_keys'
        headers = copy.deepcopy(self.headers)
        headers["Content-Type"] = "application/json"
        return post(url, data, headers)

    def del_deploykey(self, deploykey_id):
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/deploy_keys/' + str(deploykey_id)
        return delete(url, self.headers)

    def disable_deploykey(self, deploykey_id):
        url = self.url + 'api/v3/projects/' + str(self.project_id) + '/deploy_keys/' + str(deploykey_id) + '/disable'
        return delete(url, self.headers)


def post_webhook(p, url):
    print "Post webhook %s" % url
    w_data = {'url':url,'push_events':'true'}
    print p.post_webhook(w_data)

def check_exist_webhooks(res, webhook_url):
    l = []
    for i in webhook_url:
        for j in res:
            if i == j['url']:
                print "Webhook %s already exists in project %s" % (i, proj)
                l.append(i)
    return l



if __name__ == '__main__':
    names = ['bis_dx', 'kingkong']
    webhook_url = ['http://10.3.104.151:8000']

    # Here needs a config to get info below
    info = json.load(open("config.json"))['gitlab']
    gitlab_host = info['host']
    ssh_key = info['key']
    token = info['token']

    for proj in names:
        p = Project(proj, gitlab_host, token)
        if not p.project_id:
            continue

        # Post webhook
        res = p.list_webhooks()
        if res:
            l = check_exist_webhooks(res, webhook_url)
            for i in webhook_url:
                if i not in l:
                    post_webhook(p, i)
        else:
            for i in webhook_url:
                post_webhook(p, i)


        # Post deploykey
        res = p.list_deploykeys()
        if res:
            for i in res:
                if str(i[u'key']) == ssh_key:
                    print "Deploykey already exists in project %s" % proj
                else:
                    print "Post deploykey for project: %s" % proj
                    d_data = {"title": "My deploy key", "key": ssh_key}
                    print p.post_deploykey(d_data)
        else:
            print "Post deploykey"
            d_data = {"title": "My deploy key", "key": ssh_key}
            print p.post_deploykey(d_data)

