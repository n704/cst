from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

class SumView(View):

    def get(self, request, *args, **kwargs):
        """
        """
        import boto3, os, json
        query = request.GET.get('query')
        description = request.GET.get('description')
        QUEUE_URL = os.environ.get('QUEUE_URL')
        QUEUE_PORT = os.environ.get('QUEUE_PORT')
        QUEUE_NAME = os.environ.get('QUEUE_NAME')
        client = boto3.resource('sqs',
                                endpoint_url='http://{0}:{1}/'.format(QUEUE_URL, QUEUE_PORT),
                                region_name='elasticmq',
                                aws_secret_access_key='x',
                                aws_access_key_id='x',
                                use_ssl=False)
        queue = client.get_queue_by_name(QueueName=QUEUE_NAME)
        jira = JiraServer()
        jira_response = jira.make_api_call(query)
        totalPoints = 0
        message = {
            "description": description,
            "totalPoints": totalPoints
        }
        queue.send_message(MessageBody=json.dumps(message))
        return JsonResponse({"hello": jira_response})


class JiraServer(object):

    def get_json_response(self, response):
        return response.json()

    def make_api_call(self, query):
        import requests,sys, os
        JIRA_SERVER_URL=os.environ.get('JIRA_SERVER_URL')
        JIRA_PORT=os.environ.get('JIRA_PORT')
        JIRA_URL=os.environ.get('JIRA_URL')
        url = "http://{0}:{1}{2}{3}".format(JIRA_SERVER_URL,JIRA_PORT,JIRA_URL,query)
        response = requests.get(url)
        return self.get_json_response(response)
