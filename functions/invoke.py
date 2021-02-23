"""
Util function to invoke a lambda function
"""
import boto3


def invoke_lambda(function_name, invoke_type, payload):
    """
    Invokes other lambda functions

    Parameters:
        function_name: lambda function
        invoke_type: EVENT if it's an async call - RequestResponse is synced. Waits for response
        payload: event data
    """
    client = boto3.client("lambda")
    client.invoke(
        FunctionName=function_name, InvocationType=invoke_type, Payload=payload
    )
