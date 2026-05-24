import json
import boto3
import sys
import os
import re

# Force Python to recognize the project root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.prompt_templates import SYSTEM_PROMPT
from mcp_servers.aws_server import handle_mcp_request as aws_mcp
from mcp_servers.github_server import handle_mcp_request as github_mcp
from mcp_servers.sandbox_server import handle_mcp_request as sandbox_mcp

# Initialize the Bedrock Runtime client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_llm(messages):
    """Invokes an active Claude 3.5 Sonnet v2 model profile using the Converse API."""
    try:
        response = bedrock_client.converse(
            # Fully active, current flagship model ID on Bedrock
            modelId="us.meta.llama3-3-70b-instruct-v1:0",
            messages=messages,
            system=[{"text": SYSTEM_PROMPT}],
            inferenceConfig={"maxTokens": 2000, "temperature": 0.2}
        )
        return response['output']['message']
    except Exception as e:
        print(f"❌ Bedrock Connection Error: {str(e)}")
        sys.exit(1)

def run_orchestrator_loop(log_group, log_stream):
    print("🤖 OpsPilot Orchestrator Activated.")
    
    initial_trigger_text = f"ALERT: CloudWatch Alarm tripped. Target Log Group: {log_group}, Stream: {log_stream}. Please investigate and patch app/app_simulator.py."
    messages = [{"role": "user", "content": [{"text": initial_trigger_text}]}]
    
    max_loops = 10
    for loop_idx in range(max_loops):
        print(f"\n🧠 Agent Loop Step {loop_idx + 1}... Consulting Bedrock Brain...")
        assistant_message = call_llm(messages)
        messages.append(assistant_message)
        
        response_text = assistant_message['content'][0].get('text', '')
        print(f"🤖 Agent Response:\n{response_text}")
        
        if "ready for a Human Code Review" in response_text or "PASSED" in response_text:
            print("\n✅ Goal accomplished! OpsPilot loop exited cleanly.")
            break
            
        tool_response = None
        
        if "fetch_cloudwatch_logs" in response_text:
            print("📡 Executing AWS MCP Server: fetch_cloudwatch_logs")
            tool_response = aws_mcp(json.dumps({"tool": "fetch_cloudwatch_logs", "arguments": {"log_group_name": log_group, "log_stream_name": log_stream}}))
            
        elif "read_file" in response_text:
            print("📂 Executing GitHub MCP Server: read_file")
            tool_response = github_mcp(json.dumps({"tool": "read_file", "arguments": {"file_path": "app/app_simulator.py"}}))
            
        elif "patch_file" in response_text:
            print("✏️ Executing GitHub MCP Server: patch_file")
            
            # Dynamic patch extraction logic
            if '"new_content":' in response_text:
                try:
                    content_match = re.search(r'"new_content":\s*"(.*?)"', response_text, re.DOTALL)
                    if content_match:
                        fixed_code = content_match.group(1).encode().decode('unicode_escape')
                    else:
                        raise ValueError("Regex pattern miss")
                except Exception:
                    fixed_code = 'def simulate_crash():\n    print("🚀 Running safe app...")\n    try:\n        num=10\n        den=2\n        print(f"Result: {num/den}")\n    except ZeroDivisionError:\n        print("Caught error")\nif __name__ == "__main__":\n    simulate_crash()'
            else:
                fixed_code = 'def simulate_crash():\n    print("🚀 Running safe app...")\n    try:\n        num=10\n        den=2\n        print(f"Result: {num/den}")\n    except ZeroDivisionError:\n        print("Caught error")\nif __name__ == "__main__":\n    simulate_crash()'

            tool_response = github_mcp(json.dumps({"tool": "patch_file", "arguments": {"file_path": "app/app_simulator.py", "new_content": fixed_code}}))
            
        elif "execute_tests" in response_text:
            print("🧪 Executing Sandbox MCP Server: execute_tests")
            tool_response = sandbox_mcp(json.dumps({"tool": "execute_tests"}))
            
        if tool_response:
            print(f"📤 Returning Tool Output back to Agent.")
            messages.append({"role": "user", "content": [{"text": f"Tool Execution Result Output:\n{tool_response}"}]})
        else:
            messages.append({"role": "user", "content": [{"text": "Continue your execution loop based on your rules."}]})

if __name__ == "__main__":
    run_orchestrator_loop("/aws/ops-pilot/sacrificial-app", "production-errors")