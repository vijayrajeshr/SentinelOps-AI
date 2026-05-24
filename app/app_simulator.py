import datetime
import traceback
import boto3

client = boto3.client('logs', region_name='us-east-1')
LOG_GROUP = '/aws/ops-pilot/sacrificial-app'
LOG_STREAM = 'production-errors'

def simulate_crash():
    """Simulates a brand new out-of-bounds list error."""
    print("🚀 Running app simulator...")
    try:
        # 💥 YOUR NEW ERROR: Asking for an index that doesn't exist
        arr = [2, 3]
        print(arr[15]) 
        
    except Exception as e:
        print("💥 App crashed! Formatting stack trace...")
        error_stack = traceback.format_exc()
        
        log_message = (
            f"[CRITICAL ERROR] RequestID: 99f9999f-999f-99f9-999f-999f999f999f\n"
            f"Timestamp: {datetime.datetime.now(datetime.UTC).isoformat()}\n"
            f"Details: {error_stack}"
        )
        
        client.put_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=LOG_STREAM,
            logEvents=[
                {
                    'timestamp': int(datetime.datetime.now(datetime.UTC).timestamp() * 1000),
                    'message': log_message
                }
            ]
        )
        print(f"📡 Stack trace pushed to CloudWatch Log Group: {LOG_GROUP}")

if __name__ == "__main__":
    simulate_crash()