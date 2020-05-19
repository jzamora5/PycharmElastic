""" Flask Test with Dynamo DB for Elastic Beanstalk"""
import boto3
import simplejson as json
from flask import Flask, Response
from flask_cognito import cognito_auth_required
from flask_cognito import CognitoAuth


application = Flask(__name__)

application.config.update({
    'COGNITO_REGION': 'us-east-1',
    'COGNITO_USERPOOL_ID': '',

    # optional
    'COGNITO_APP_CLIENT_ID': '',  # client ID you wish to verify user is authenticated against
    'COGNITO_CHECK_TOKEN_EXPIRATION': False,  # disable token expiration checking for testing purposes
    'COGNITO_JWT_HEADER_NAME': 'X-MyApp-Authorization',
    'COGNITO_JWT_HEADER_PREFIX': 'Bearer'
})


cogauth = CognitoAuth(application)


def jsonify(obj):
    json_st = json.dumps(obj)
    return Response(json_st, mimetype='application/json')


def create_table(ddb_create):
    table_created = ddb_create.create_table(
        TableName='Test_Table',

        KeySchema=[
            {
                'AttributeName': 'user_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'last_name',
                'KeyType': 'RANGE'
            }
        ],

        AttributeDefinitions=[
            {
                'AttributeName': 'user_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            }
        ],

        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table_created.meta.client.get_waiter('table_exists').wait(TableName='Test_Table')


@application.route('/')
@cognito_auth_required
def hello_world():
    response = table.get_item(
        Key={
            'user_name': 'Amber',
            'last_name': 'Corn'
        }
    )
    item = response['Item']

    return jsonify(item)


ddb = boto3.resource('dynamodb', region_name='us-east-1')
ddbC = boto3.client('dynamodb', region_name='us-east-1')
table_name = 'Test_Table'
table = ddb.Table(table_name)
existing_tables = ddbC.list_tables()['TableNames']
if table_name not in existing_tables:
    create_table(ddb)
    table = ddb.Table(table_name)
    table.put_item(
        TableName=table_name,
        Item={
            'user_name': 'Larry',
            'last_name': 'Berlton',
            'age': 26
        }
    )

    table.put_item(
        TableName=table_name,
        Item={
            'user_name': 'Amber',
            'last_name': 'Corn',
            'age': 25
        }
    )

if __name__ == '__main__':
    application.run()
