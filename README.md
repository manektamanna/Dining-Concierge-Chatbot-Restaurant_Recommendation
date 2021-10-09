# Dining-Concierge-Chatbot-Restaurant_Recommendation

This is a Amazon Web Service-based chatbot that recommends restaurants to users on the basis of entered requirements such as - Number of people, Cuisine, Time of the day, etc provided via interactive conversations. Several microservices were used in synergy to create this serverless, microservice-driven web application prototype.<br/>

We gather all of our code here. Note that the code here cannot be run directly because we use AWS to delopy this application. Almost half of the work is to create and configure AWS components. The used AWSs are listed as followings:<br/>

**AWS S3**

● It stores all frontend files in a bucket. All HTML,CSS and Js files are stored in the created S3 bucket.<br/>
● Link to run the chatbot --> http://baltias1.s3-website-us-east-1.amazonaws.com
*Amazon Simple Storage Service (Amazon S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance.*<br/>

**Amazon API Gateway** (RESTful APIs)

● API Gateway can generate an SDK for your API, which can be used in the frontend. It will take care of calling your API, as well as session signing the API calls.<br/>
*Amazon API Gateway is a fully managed service that makes it easy for developers to create, publish, maintain, monitor, and secure APIs at any scale. APIs act as the "front door" for applications to access data, business logic, or functionality from your backend services. Using API Gateway, you can create RESTful APIs and WebSocket APIs that enable real-time two-way communication applications. API Gateway supports containerized and serverless workloads, as well as web applications.*

**AWS Lambda function**

● Lamda functions handle request from front-end.<br/>
● In our project we have total 3 lambda functions. <br/>
1) LF0 is connected with API gateway and lambda - Receives requests from API gateway and sends to Lex.<br/>
2) LF1  helps Lex in returning the response, handling the cases and connecting the obtained values.<br/>
3) LF2 for searching in elastic search and returning the restaurant suggestion. LF1 also handles the part  when a successful requests is made to Lex (all intents get filled up) will add the request in SQS (Simple Queue Service). SQS will trigger LF2.<br/>
*AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers, creating workload-aware cluster scaling logic, maintaining event integrations, or managing runtimes.*<br/>

**Amazon Lex**
1) Implement at least the following three intents:<br/>
● GreetingIntent<br/>
● ThankYouIntent<br/>
● DiningSuggestionsIntent<br/>
2) The implementation of an intent entails its setup in Amazon Lex as well as handling its response in the Lambda function code hook.<br/>
● Example: for the GreetingIntent you need to 1. create the intent in Lex, 2. train and test the intent in the Lex console, 3. implement the handler for the GreetingIntent in the Lambda code hook, such that when you receive a request for the GreetingIntent you compose a response such as “Hi there, how can I help?”<br/>
3). For the DiningSuggestionsIntent, you need to collect at least the following pieces of information from the user, through conversation:<br/>
● Location<br/>
● Cuisine<br/>
● Dining Time<br/>
● Number of people<br/>
● Phone number<br/>
4) Based on the parameters collected from the user, push the information collected from the user (location, cuisine, etc.) to an SQS queue (Q1). More on SQS queues here:<br/> https://aws.amazon.com/sqs/<br/>
● Also confirm to the user that you received their request and that you will notify them over Email once you have the list of restaurant suggestions.<br/>
 *Amazon Lex a service for building conversational interfaces into any application using voice and text.*<br/>
 
**Amazon SQS**

● Stores user response in a queue which we can pull in another Lambda function to match with out dynamoDB table.<br/>
*Amazon Simple Queue Service (SQS) is a fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.*<br/>

**Amazon DynamoDB**

● Create a DynamoDB table and named “yelp-restaurants”<br/>
● Store the restaurants you scrape, in DynamoDB (one thing you will notice is that some restaurants might have more or less fields than others, which makes DynamoDB ideal for storing this data)<br/>
● With each item you store, make sure to attach a key to the object named “insertedAtTimestamp” with the value of the time and date of when you inserted the particular record.<br/>
● Store those that are necessary for your recommendation. (Requirements: Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code).<br/>
*Amazon DynamoDB is a fully managed, serverless, key-value NoSQL database designed to run high-performance applications at any scale.*<br/>

**Amazon OpenSearch Service (successor to Amazon Elasticsearch Service)**

● Create an ElasticSearch index called “restaurants”<br/>
● Create an ElasticSearch type under the index “restaurants” called “Restaurant”<br/>
● Store partial information for each restaurant scraped in ElasticSearch under the “restaurants” index, where each entry has a “Restaurant” data type.<br/>
● You only need to store RestaurantID and Cuisine for each restaurant.<br/>


###### Architecture View 
<br/><br/>
<p style="text-align:center;"><img width="929" alt="Assignment 1 architecture diagram (2)" src="https://user-images.githubusercontent.com/85683392/136674276-74ab5584-40a6-445a-abe0-b5de49488c19.png">

###### Screenshots
 

![Screenshot (184)__01](https://user-images.githubusercontent.com/85683392/136675108-bca50815-a9d4-43b7-83ab-be107b375e84.png)
![Screenshot (185)__01](https://user-images.githubusercontent.com/85683392/136675113-da6b00c6-e131-4aed-b938-48658b86637c.png)
![Screenshot (186)__01](https://user-images.githubusercontent.com/85683392/136675115-23f529d7-bac5-42a6-aeb4-f8c36bde4868.png)
![Screenshot (187)__01](https://user-images.githubusercontent.com/85683392/136675118-97904a12-715b-469a-8891-6a0acfd36a30.png)


