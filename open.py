import logging as logger
import base64
from awssec import SecretManager
from pydantic import BaseModel
from openai import AzureOpenAI
import requests
import asyncio

try:
    logger.basicConfig(level="INFO")
    secret = SecretManager()
    open_ai_secrets = secret.get_aws_secret_dict("azureopenai")
    AZURE_ENDPOINT = open_ai_secrets["azure_endpoint"]
    AZURE_API_KEY = open_ai_secrets["api_key"]
    DEPLOYMENT_NAME = open_ai_secrets["deployment_name"]
except Exception as err:
    logger.error(err)
    

def decode_base64_body(slack_body):
    """Decodes the base64 encoded body of the slack request"""
    try:
        base64_bytes = slack_body.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("ascii")
        return sample_string
    except Exception as err:
        logger.error(err)


def format_query(my_str, sub, side):
    """Removes everything before/after a specific character"""
    try:
        index=my_str.find(sub)
        if index !=-1:
            if side == 'left':
                return my_str[index:]
            elif side == 'right':
                return my_str[:index]
        else:
            raise Exception('Sub string not found!')
    except Exception as err:
        logger.error(err)


def format_punctuation(query):
    """Converts URL encoded characters to normal punctuation"""
    try:
        query = query.replace("+", " ")
        query = query.replace("%22", "'")
        query = query.replace("%3F", "?")
        query = query.replace("%21", "!")
        query = query.replace("%2C", ",")
        return query
    except Exception as err:
        logger.error(err)
    
    
async def lambda_handler(event, context):
    """Processes events, formats the slack query and sends it over to Azure OpenAI"""
    try:
        slack_body = event.get("body")
        encoded_body = decode_base64_body(slack_body)

        formatting_query = format_query(encoded_body, "&text", "left")
        formatting_query_2 = format_query(formatting_query, "&api", "right")
        formatting_query_3 = format_query(formatting_query_2, "=", "left")
        formatting_query_3 = (formatting_query_3[1:])
        open_ai_query = format_punctuation(formatting_query_3)

        #logger.info(f"Open AI Query: {open_ai_query}")

        client = AzureOpenAI(
            azure_endpoint = AZURE_ENDPOINT, 
            api_key = AZURE_API_KEY,  
            api_version="2023-05-15",
        )

        model = "azure-data-openai-service-gpt-4-test"
        response = client.chat.completions.create(model=model, messages = [{"role":"system", "content":"You are a helpful assistant."}, {"role":"user","content":open_ai_query},])
        generated_response = response.choices[0].message.content

        #logger.info(f"Open AI Response: {response}")
        #logger.info(f"Generated Response: {generated_response}")

        return {'statusCode': 200, 'body': generated_response}

    except Exception as err:
        logger.error(err)
        
event = {
  "headers": {
    "content-length": "442",
    "x-amzn-tls-version": "TLSv1.3",
    "x-forwarded-proto": "https",
    "x-forwarded-port": "443",
    "x-forwarded-for": "54.204.153.42",
    "accept": "application/json,/",
    "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
    "x-amzn-trace-id": "Root=1-6846dc9d-544ba4c9765c82d63ee8ea42",
    "host": "qb56sq26metxtmwlr2bwljdmfy0fndjh.lambda-url.eu-west-1.on.aws",
    "content-type": "application/x-www-form-urlencoded",
    "x-slack-request-timestamp": "1749474461",
    "x-slack-signature": "v0=8e3af8eec9967837ef49857a2523f889068fa93f76cc3f6abfbcb8b1598e0f17",
    "accept-encoding": "gzip,deflate",
    "user-agent": "Slackbot 1.0 (+https://api.slack.com/robots)"
  },
  "isBase64Encoded": True,
  "rawPath": "/",
  "routeKey": "$default",
  "requestContext": {
    "accountId": "anonymous",
    "timeEpoch": 1749474461916,
    "routeKey": "$default",
    "stage": "$default",
    "domainPrefix": "qb56sq26metxtmwlr2bwljdmfy0fndjh",
    "requestId": "19b06c1b-711c-40a8-b74e-19279d8e7149",
    "domainName": "qb56sq26metxtmwlr2bwljdmfy0fndjh.lambda-url.eu-west-1.on.aws",
    "http": {
      "path": "/",
      "protocol": "HTTP/1.1",
      "method": "POST",
      "sourceIp": "54.204.153.42",
      "userAgent": "Slackbot 1.0 (+https://api.slack.com/robots)"
    },
    "time": "09/Jun/2025:13:07:41 +0000",
    "apiId": "qb56sq26metxtmwlr2bwljdmfy0fndjh"
  },
  "body": "dG9rZW49WkNCSzNhUkNGcHhzZmczcmd3R0RnaDNDJnRlYW1faWQ9VDFLNVpIQVExJnRlYW1fZG9tYWluPWVzdXJlZ3JvdXAmY2hhbm5lbF9pZD1DMDUzMzBKNkxNUiZjaGFubmVsX25hbWU9ZGV2c2Vjb3BzLXRlYW0mdXNlcl9pZD1VMDhFVzUwMFRMRyZ1c2VyX25hbWU9d2lsbC5zaGVwaGVyZCZjb21tYW5kPSUyRnNlbmRfcXVlcnlfbGFtYmRhJnRleHQ9JTIySmFzb24lMjImYXBpX2FwcF9pZD1BMDkwTFI2TkRDSiZpc19lbnRlcnByaXNlX2luc3RhbGw9ZmFsc2UmcmVzcG9uc2VfdXJsPWh0dHBzJTNBJTJGJTJGaG9va3Muc2xhY2suY29tJTJGY29tbWFuZHMlMkZUMUs1WkhBUTElMkY5MDIxODIxNzM4ODg0JTJGbVMzbmlrTU9WUXBWeUw2dDgxV2RJMG9RJnRyaWdnZXJfaWQ9OTAyMTgyMTc1MjI5Mi41MzIwMzU4ODgxNy5iNzg2MTBlZWQ2NzIxZDk0MmYzZGU0MDZjNGFjMzA1ZQ==",
  "version": "2.0",
  "rawQueryString": ""
}

asyncio.run(lambda_handler(event,1))