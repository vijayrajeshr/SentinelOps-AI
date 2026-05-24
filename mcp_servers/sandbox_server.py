import json
import subprocess
import sys
import os

def run_local_tests():
    """
    Executes the repository test suite via pytest and returns 
    the raw stdout/stderr logs directly back to the AI agent.
    """
    try:
        # Check if pytest is installed, default to python standard unittest if not
        # For simplicity and reliability in your demo, we execute via python -m unittest
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        if result.returncode == 0:
            return {"status": "PASSED", "output": output}
        else:
            return {"status": "FAILED", "output": output}
            
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "output": "Test execution exceeded 30 seconds."}
    except Exception as e:
        return {"status": "ERROR", "output": str(e)}

def handle_mcp_request(json_input):
    try:
        payload = json.loads(json_input)
        tool_name = payload.get("tool")

        if tool_name == "execute_tests":
            test_result = run_local_tests()
            return json.dumps({"status": "success", "result": test_result})
        else:
            return json.dumps({"error": f"Unknown Sandbox MCP tool: {tool_name}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to parse Sandbox MCP request: {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(handle_mcp_request(sys.argv[1]))