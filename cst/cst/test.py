from django.test import TestCase
from cst.views import *
from mock import patch, Mock, MagicMock
from requests.exceptions import ConnectionError
import requests

class JiraServerTestCase(TestCase):


    @patch('requests.get', side_effect=ConnectionError)
    def test_jira_connect(self, mock_get):
        """test connect to server and response. """
        jira = JiraServer()
        self.assertRaises(StoryPointsCalculatorError, lambda : jira.make_api_call(''))


    def test_jira_request(self):
        """get requests"""
        jira = JiraServer()
        mock = Mock()
        mock.json = MagicMock(return_value=list([]))
        with patch.object(requests, 'get', return_value=mock) as mock_method:
            self.assertEquals(jira.make_api_call('type=Bug'), [])

class SQSTestCase(TestCase):

    def test_init(self):
        import boto3
        from botocore.exceptions import EndpointConnectionError
        mock = Mock()
        mock.get_queue_by_name = Mock(side_effect=lambda QueueName: EndpointConnectionError())
        with patch.object(boto3, 'resource', return_value=mock) as mock_method:
            self.assertRaises(SQSError, lambda : SQS())


class StoryPointsCalculatorTestCase(TestCase):

    def test_get_score(self):
        story_cal = StoryPointsCalculator('')
        mock = []
        with patch.object(JiraServer, 'make_api_call', return_value=mock) as mock_method:
            self.assertEquals(story_cal.get_score(), 0)
        mock = [{"a": 1}]
        with patch.object(JiraServer, 'make_api_call', return_value=mock) as mock_method:
            self.assertRaises(NoDataError, lambda: story_cal.get_score())

        mock = [{"fields":{"storyPoints": 9999}}]
        with patch.object(JiraServer, 'make_api_call', return_value=mock) as mock_method:
            self.assertEquals(story_cal.get_score(), 9999)


class SumViewTestCase(TestCase):

    @patch('cst.views.SQS')
    def test_get(self, mock_sqs):
        import json
        mock = Mock()
        mock.GET = {}
        sum_view = SumView()
        res = sum_view.get(mock)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content)["error"], "No query")
        mock.GET = {'query': '1'}
        res = sum_view.get(mock)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(json.loads(res.content)["error"], "No description")
        mock.GET = {'query': '1', 'description': '1'}
        # testing StoryPointsCalculator
        def test_err():
            raise StoryPointsCalculatorError("StoryPointsCalculatorError")
        storyPoints = StoryPointsCalculator('')
        with patch.object(StoryPointsCalculator, "get_score", side_effect=test_err) as mock_method:
            res = sum_view.get(mock)
            self.assertEquals(res.status_code, 400)
            self.assertEquals(json.loads(res.content)["error"], "StoryPointsCalculatorError")
        def test_err():
            raise NoDataError("NoDataError")
        storyPoints = StoryPointsCalculator('')
        with patch.object(StoryPointsCalculator, "get_score", side_effect=test_err) as mock_method:
            res = sum_view.get(mock)
            self.assertEquals(res.status_code, 400)
            self.assertEquals(json.loads(res.content)["error"], "NoDataError")
            def test_err():
                return 0
            storyPoints = StoryPointsCalculator('')
            def sqs_error(x):
                raise SQSError("SQSError")
            mock_send = Mock()
            mock_send.send_json_message = sqs_error
            mock_sqs.return_value = mock_send

            with patch.object(StoryPointsCalculator, "get_score", side_effect=test_err) as mock_method:
                res = sum_view.get(mock)
                self.assertEquals(res.status_code, 400)
                self.assertEquals(json.loads(res.content)["error"], "SQSError")

            mock_send = Mock()
            mock_send.send_json_message = lambda x: 1
            mock_sqs.return_value = mock_send
            with patch.object(StoryPointsCalculator, "get_score", side_effect=test_err) as mock_method:
                res = sum_view.get(mock)
                self.assertEquals(res.status_code, 200)
                self.assertEquals(json.loads(res.content)["success"], {"totalPoints": 0, "description": "1"})
