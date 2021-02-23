import os
import boto3


class AwsUtils:
    """Utils class to deal with various aws actions"""

    @staticmethod
    def get_dynamodb_client():
        IS_OFFLINE = os.environ.get("IS_OFFLINE")

        if IS_OFFLINE:
            dynamo_client = boto3.client(
                "dynamodb",
                region_name="localhost",
                endpoint_url="http://localhost:8000",
            )
        else:
            dynamo_client = boto3.client("dynamodb")

        return dynamo_client

    @staticmethod
    def get_dynamodb_resource():
        IS_OFFLINE = os.environ.get("IS_OFFLINE")

        if IS_OFFLINE:
            dynamo_resource = boto3.resource(
                "dynamodb",
                region_name="localhost",
                endpoint_url="http://localhost:8000",
            )
        else:
            dynamo_resource = boto3.resource("dynamodb")

        return dynamo_resource
