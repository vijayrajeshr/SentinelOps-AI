import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Receives an EventBridge state-change event for the CloudWatch alarm,
    extracts the failure context, and prepares it for the Bedrock Agent.
    """
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        # Extract metadata from the CloudWatch Alarm event pattern
        detail = event.get('detail', {})
        alarm_name = detail.get('alarmName', 'Unknown-Alarm')
        new_state = detail.get('state', {}).get('value', 'UNKNOWN')
        reason = detail.get('state', {}).get('reason', 'No reason provided.')
        
        logger.info(f"Alarm '{alarm_name}' transitioned to state: {new_state}")
        
        # Hardcoded payload targets for our specific local simulation
        # In a full production app, you can parse these details dynamically out of the 'reason' string
        job_context = {
            "status": "TRIGGERED",
            "alarm_name": alarm_name,
            "state_change_reason": reason,
            "target_log_group": "/aws/ops-pilot/sacrificial-app",
            "target_log_stream": "production-errors"
        }
        
        logger.info("Context parsed successfully. Ready for Bedrock Agent invocation.")
        
        # TODO: Phase 3 will inject the Amazon Bedrock Agent invocation client right here.
        # client = boto3.client('bedrock-agent-runtime')
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Event ingested and processed successfully.',
                'context': job_context
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing ingestion event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal processing error'})
        }
        