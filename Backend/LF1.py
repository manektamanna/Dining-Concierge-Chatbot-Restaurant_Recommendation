
import math
import dateutil.parser
import datetime
import time
import os
import logging
import json 
import boto3
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#This functions gets the user inputs from Lex in form of slots and then sends it to SQS queue
def send_recommendations(intent_request):
    client = boto3.client('sqs')
    slots = intent_request['currentIntent']['slots']
    location = get_slots(intent_request)["Location"]
    cuisine = get_slots(intent_request)["Cuisine"]
    people = get_slots(intent_request)["People"]
    date  =  get_slots(intent_request)["Date"]
    time  =  get_slots(intent_request)["Time"]
    phoneno = get_slots(intent_request)["PhoneNo"]
    email= get_slots(intent_request)["Email"]
    response = client.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/791963637204/Q1',
        MessageAttributes={
                    'cuisine': {
                        'DataType': 'String',
                        'StringValue': cuisine
                    },
                    'location': {
                        'DataType': 'String',
                        'StringValue': location
                    },
                    'people': {
                        'DataType': 'String',
                        'StringValue': people
                    },
                    'date': {
                        'DataType': 'String',
                        'StringValue': date
                    },
                    'time': {
                        'DataType': 'String',
                        'StringValue': time
                    },
                    'phoneno': {
                        'DataType': 'String',
                        'StringValue': phoneno
                    },
                    'email': {
                        'DataType': 'String',
                        'StringValue': email
                    }
            
        },
        MessageBody=("user"),
    )
    print(response)
    logger.debug("SQS mssg sent")


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False
        
def is_after_now(date, time):
    return (dateutil.parser.parse(date).date() > datetime.date.today()) or (
            dateutil.parser.parse(date).date() == datetime.date.today() and dateutil.parser.parse(
        time).time() > datetime.datetime.now().time())
        
def isvalid_phone(phone):
    return len(phone) == 10
    
def isvalid_email(email):
    if(email.endswith('nyu.edu') or email.endswith('gmail.com')):
        return True
    return False

#This function validates the inputs entered by the user
def validate_user_inputs(location,cuisine,people,date,time,phoneno,email):
    cities = ['manhattan']
    print(location)
    valid_cuisines=['italian','american','japanese','chinese','mexican']
    valid_people=['1','2','3','4','5','6','7','8','9','10','one','two','three','four','five','six','seven','eight','nine','ten']
    if location is not None and location.lower() not in cities:
        return build_validation_result(False,
                                       'Location',
                                       'That is a beautiful place. Unfortunately, we only suggest restaurants in the Manhattan area in New York City. Currently, we are not covering {} area but look forward to it!'.format(location))
                                       

    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'Date', 'I did not understand that, what date would you like to book the reservation for?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Date', 'You cannot choose a date from the past (Time travel doesnt exists. YET!). Choose today or future date')

    if cuisine is not None and cuisine.lower() not in valid_cuisines :
        return build_validation_result(False, 'Cuisine','We have Italian, American, Japanese, Chinese and Mexican cusines. Sounds delicious, right? Though we will add more options soon')
        
    if time is not None and date is not None:
        if not is_after_now(date, time):
            return build_validation_result(False,'Time','Please enter future time. Suggestions cannot be given for the time in past (no time travel?)')
            
    if phoneno is not None:
        if not isvalid_phone(phoneno):
            return build_validation_result(False,'PhoneNo','PhoneNo. cant be greater than 10')
            

    if people is not None and people not in valid_people:
        return build_validation_result(
             False,
             'People',
             'No. of people can only be greater than 1 and less than 10'
         )
    if email is not None:
        if not isvalid_email(email):
            return build_validation_result(False,'Email','Please enter valid Email Address')
        
            
    

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def suggest_restaurants(intent_request):
   

    location = get_slots(intent_request)["Location"]
    cuisine = get_slots(intent_request)["Cuisine"]
    people = get_slots(intent_request)["People"]
    date  =  get_slots(intent_request)["Date"]
    time  =  get_slots(intent_request)["Time"]
    phoneno = get_slots(intent_request)["PhoneNo"]
    email= get_slots(intent_request)["Email"]
    source = intent_request['invocationSource']
  
   
    if intent_request['invocationSource'] == 'DialogCodeHook':
        logger.debug('invocationSource={}'.format(intent_request['invocationSource']))
        slots = get_slots(intent_request)
        validation_result = validate_user_inputs(location,cuisine,people,date,time,phoneno,email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
                               

        
        return delegate(intent_request['sessionAttributes'], get_slots(intent_request))
        
    if intent_request['invocationSource'] == 'FulfillmentCodeHook':
        logger.debug('invocationSource={}'.format(intent_request['invocationSource']))
        send_recommendations(intent_request)
        
    
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'You\'re all set. Expect my suggestions shortly'})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return suggest_restaurants(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    print(event)

    return dispatch(event)

