# CST coding exercise

## testing

`cd cst && ./manage.py test`

## building

`docker-compose build` this will create python app and elasticmq and link them.


## running

update the `cst.env` file to update url and API keys.

`docker-compose up`
This will bring both python server and elasticmq as well.

  `docker run -v "$PWD/mountebank:/imposters" -p 2525:2525 -p 4553:4553 -d expert360/mountebank --configfile /imposters/jira-api.ejs --allowInjection`

this will bring up jira mock server.





## Background

A common task in our microservice-oriented architecture is consuming a REST API from one service and transforming it into another format. To decouple the consumer and the producer services, we make use of queues, for example AWS SQS or RabbitMQ.

We frequently fetch data from Jira through its REST API to get specific fields from a list of issues and perform a transformation or calculation and post the result into a queue so other consumer can continue with processing.

## Exercise

We want you to write the code to traverse a RESTful API to calculate the sum of story points from each Issue object and post this into an SQS queue as a JSON object. Your app will need to listen on port :8080 and implement the following endpoint:

GET `/api/issue/sum?query={search_query}&name={descriptive_name}`

As you can see, you will receive query param query with value being the search query to be sent to Jira. You will use this query parameter in your call to the actual Jira interface (for the sake of simplicity we've created a fake one for you without authentication etc). The outbound call will be to:

`<Jira Base URL>/rest/api/2/search?q={search_query}`

Your application will receive the Jira Base URL as an environment variable with name `JIRA_BASE_URL`.

This endpoint searches for issues matching given query will return a list of matching issues, or an empty list with `application/json` as the content type. An example output:

```
[{
    "issueKey": "TEST-1",
    "fields": {
        "storyPoints": 1
    }
},{
    "issueKey": "TEST-2",
    "fields": {
        "storyPoints": 2
    }
}]
```

Once you sum up the story points from this list, the result should be put into into SQS in the following format (only one message for each requested query):

```
{
    "name": {descriptive_name},
    "totalPoints": {total_points}
}
```

Your application will receive the Queue URL as an environment variable with name `QUEUE_URL` and you will not need to perform any authentication to put objects into it.

## Implementation

-   We would prefer that you write this code in Java, but other languages are acceptable. You can use System.main or any framework you wish (Spring Boot, DropWizard).

-   Your code needs only to walk the api a single time, and does not need to persist across executions.
-   Assume this is a public API with NO access control
-   Serviceability and level of "production readiness" are concerns
-   Solution should not be machine or OS specific
-   You can assume that your application is authenticated to use the services (Jira and SQS)

## Mocking SQS and Jira

We understand that having a running Jira instance or an SQS might be difficult to arrange so we have decided to provide you with a simple way to use while developing your application.

1.  To use a 'mock' SQS implementation we recommend using [graze/sqs-local Docker image](https://github.com/graze/docker-sqs-local), we even provide a config file to in this repository. You can run the mock SQS implementation listening on port :9342 using

    `docker run -p 9324:9324 -v "$PWD/sqs/queue.conf:/elasticmq.conf" graze/sqs-local`

    from the root of this repository. Inspect the config file to discover your queue name/URL.

2.  To ease the development for the Jira related part, we have created mock responses using [Mountebank](http://www.mbtest.org/) in the `mountebank` folder. You can easily use any available Docker images to run the Mountebank server:

    `docker run -v "$PWD/mountebank:/imposters" -p 2525:2525 -p 4553:4553 -d expert360/mountebank --configfile /imposters/jira-api.ejs --allowInjection`

# Delivery

When you think your code is ready for the prime time, please push your work to a public repository on Bitbucket/Github/Gitlab and send us a link to it. Do not forget to provide us instruction on how to use your software. Feel free to provide any kind of feedback or explanation of your design choices.

We will be evaluating your submission by inspecting the code, and also by running your application in isolation (based on your instructions). We will be providing the HTTP/SQS endpoints as described above.
