import boto3

def lambda_handler(event, context):
    client = boto3.client('lex-runtime')
    # This post_text function sends  user message to Lex and get backs the response from it
    response = client.post_text(botName='Rest_Recommendation', botAlias='$LATEST', userId='tannu',
                                inputText=event['messages'][0]['unstructured']['text'])
    print(response)

    return {
        'statusCode': 200,
        'messages': [{
            'type': 'unstructured',
            'unstructured': {
                'text': response['message']
            }
        }]
    }
