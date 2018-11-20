from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse


class SumView(View):
    """
    View for getting total storyPoints
    """

    def get(self, request, *args, **kwargs):
        """
        GET request to get totatl storyPoints.
        """
        import json
        query = request.GET.get('query')
        description = request.GET.get('description')
        storyPoints = StoryPointsCalculator(query)
        try:
            totalPoints = storyPoints.get_score()
        except StoryPointsCalculatorError as e:
            return JsonResponse({"error": e.message}, status=400)
        except NoDataError as e:
            return JsonResponse({"error": e.message}, status=400)
        message = {
            "description": description,
            "totalPoints": totalPoints
        }
        try:
            sqs = SQS()
            sqs.send_json_message(message)
        except SQSError as e:
            return JsonResponse({"error": e.message}, status=400)
        return JsonResponse({"success": message})

class StoryPointsCalculatorError(Exception):
    def __init__(self, message):
        super(StoryPointsCalculatorError, self).__init__(message)

class NoDataError(Exception):
    def __init__(self, message):
        super(NoDataError, self).__init__(message)

class SQSError(Exception):
    def __init__(self, message):
        super(SQSError, self).__init__(message)

class JiraServer(object):
    """
    Jira Server Adaptor get API response from jira server.
    """
    def get_json_response(self, response):
        """
        return json response
        """
        try:
            return response.json()
        except ValueError:
            raise NoDataError("No Data from Server")

    def make_api_call(self, query):
        """
        Make API call and return json result
        """
        import requests
        import os
        from requests.exceptions import ConnectionError
        JIRA_SERVER_URL = os.environ.get('JIRA_SERVER_URL')
        JIRA_PORT = os.environ.get('JIRA_PORT')
        JIRA_URL = os.environ.get('JIRA_URL')
        url = "http://{0}:{1}{2}{3}".format(
            JIRA_SERVER_URL,
            JIRA_PORT,
            JIRA_URL,
            query)
        try:
            response = requests.get(url)
        except ConnectionError as e:
            raise StoryPointsCalculatorError("Connect make call to JIRA server")
        return self.get_json_response(response)

class StoryPointsCalculatorError(Exception):
    def __init__(self, message):
        super(StoryPointsCalculatorError, self).__init__(message)

class StoryPointsCalculator(object):

    def __init__(self, query):
        self.query = query

    def process_jira_response(self, jira_response):
        """
        Caluate totalPoints and returns
        @args: jira_response json response from jira
        @returns: totalPoints integer
        """
        return sum([x["fields"]["storyPoints"] for x in jira_response])

    def get_score(self):
        """
        Get score from jira server.
        """
        jira = JiraServer()
        jira_response = jira.make_api_call(self.query)
        return self.process_jira_response(jira_response)

class SQS(object):
    """
    Adaptor to connect to SQS queue
    """

    def __init__(self):
        import boto3
        import os
        from botocore.exceptions import EndpointConnectionError
        QUEUE_URL = os.environ.get('QUEUE_URL')
        QUEUE_PORT = os.environ.get('QUEUE_PORT')
        QUEUE_NAME = os.environ.get('QUEUE_NAME')
        client = boto3.resource('sqs',
            endpoint_url='http://{0}:{1}/'.format(QUEUE_URL, QUEUE_PORT),
            region_name='elasticmq',
            aws_secret_access_key='x',
            aws_access_key_id='x',
            use_ssl=False)
        try:
            self.queue = client.get_queue_by_name(QueueName=QUEUE_NAME)
        except EndpointConnectionError as e:
            raise SQSError("Cannot connect to SQS")


    def send_json_message(self, message):
        """
        @arg message: dict
        """
        import json
        self.queue.send_message(MessageBody=json.dumps(message))
