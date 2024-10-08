# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/awsUtil.ipynb (unless otherwise specified).

__all__ = ['invokeLambdaWithApigatewayProxy']

# Cell
import json
import boto3
from pprint import pprint


def invokeLambdaWithApigatewayProxy(
    payload, function_name, region_name="ap-southeast-1", debug=False, queryparams={}
):
    """
    Invokes an AWS Lambda function through the API Gateway proxy integration, with support for query parameters.

    Args:
        payload (dict): The input data to send to the Lambda function. This will be
            serialized to JSON and included in the 'body' of the request.
        function_name (str): The name of the Lambda function to invoke.
        region_name (str, optional): The AWS region where the Lambda function is deployed.
            Defaults to 'ap-southeast-1'.
        debug (bool, optional): If True, prints the raw response payload for debugging purposes.
            Defaults to False.
        query_params (dict, optional): A dictionary of query parameters to include in the request,
            as if making a GET request. These parameters are serialized and included in the request.

    Returns:
        dict: The parsed response from the Lambda function, including the 'body' key
            containing the JSON-decoded result.

    Raises:
        KeyError: If the Lambda function's response does not include a 'body' key.
        Exception: If there is an error decoding the Lambda response payload.
    """
    lambda_client = boto3.client("lambda", region_name=region_name)
    payload_json = json.dumps(
        {"body": json.dumps(payload), "queryStringParameters": queryparams}
    )
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",  # RequestResponse waits for the response, Event is async
        Payload=payload_json.encode("utf-8"),
    )
    responsePayload = response["Payload"].read().decode("utf-8")
    try:
        result = json.loads(responsePayload)
        body = json.loads(result["body"])
        result["body"] = body
        if debug:
            pprint(responsePayload)
        return result
    except KeyError as e:
        print("there is a keyerror perhaps the function failed", e)
        print("result is")
        pprint(responsePayload)
        raise (e)
    except Exception as e:
        print("decoding failed", e)
        print(result)
        pprint(responsePayload)
        raise (e)