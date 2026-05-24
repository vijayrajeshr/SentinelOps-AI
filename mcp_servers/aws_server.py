import json
import sys
import boto3
from botocore.exceptions import ClientError

# Initialize the AWS logs client
logs_client = boto3.client('logs', region_name='us-east-1')

def fetch_cloudwatch_logs(log_group_name, log_stream_name, limit=50):
    """Queries AWS CloudWatch to grab the exact stack trace surrounding the crash."""
    try:
        response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            limit=limit,
            startFromHead=False
        )
        events = response.get('events', [])
        log_lines = [event.get('message', '') for event in events]
        return "\n".join(log_lines)
    except ClientError as e:
        return f"Error retrieving logs from AWS: {e.response['Error']['Message']}"

def handle_mcp_request(json_input):
    """MCP Protocol Wrapper: Standardizes communication for the Bedrock Agent."""
    try:
        data = json.loads(json_input)
        tool_name = data.get("tool")
        arguments = data.get("arguments", {})

        if tool_name == "fetch_cloudwatch_logs":
            log_group = arguments.get("log_group_name")
            log_stream = arguments.get("log_stream_name")
            
            if not log_group or not log_stream:
                return json.dumps({"error": "Missing required arguments: log_group_name, log_stream_name"})
            
            log_output = fetch_cloudwatch_logs(log_group, log_stream)
            return json.dumps({"status": "success", "data": log_output})
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to parse or execute MCP request: {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(handle_mcp_request(sys.argv[1]))