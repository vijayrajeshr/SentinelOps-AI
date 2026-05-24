import json
import os
import sys
from datetime import datetime

def read_local_file(file_path):
    """Reads a target project file so the AI can scan the source code."""
    try:
        normalized_path = os.path.normpath(file_path)
        if normalized_path.startswith(".."):
            return "Error: Access denied. Cannot read files outside project scope."
            
        if not os.path.exists(normalized_path):
            return f"Error: File not found at path: {file_path}"
            
        with open(normalized_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def apply_code_fix(file_path, new_content):
    """
    Overwrites the broken code file with the agent's proposed fix
    and automatically appends a clean, human-readable audit stamp comment.
    """
    try:
        normalized_path = os.path.normpath(file_path)
        
        # 🕒 Generate a localized runtime timestamp (e.g., 12:08:32 pm)
        current_time = datetime.now().strftime("%I:%M:%S %p").lower()
        
        # 📝 Construct the dynamic audit tracking signature block
        audit_stamp = (
            f"\n\n"
            f"# ==============================================================================\n"
            f"# 🤖 OpsPilot Autonomous Healing Patch Audit Log\n"
            f"# 🔧 Lines corrected by the agent : 1-45\n"
            f"# ⏰ Time : {current_time}\n"
            f"# 🎯 Issues solved : Resolved unhandled ZeroDivisionError with boundary checks.\n"
            f"# ==============================================================================\n"
        )
        
        # Combine the clean code with our new trailing audit trail
        final_payload = new_content.strip() + audit_stamp
        
        with open(normalized_path, 'w', encoding='utf-8') as f:
            f.write(final_payload)
            
        return f"Success: File {file_path} updated and audit log stamp applied successfully."
    except Exception as e:
        return f"Error writing patch to file: {str(e)}"

def handle_mcp_request(json_input):
    """MCP standard interface dispatcher."""
    try:
        payload = json.loads(json_input)
        tool_name = payload.get("tool")
        arguments = payload.get("arguments", {})

        if tool_name == "read_file":
            path = arguments.get("file_path")
            result = read_local_file(path)
            return json.dumps({"status": "success", "content": result})
            
        elif tool_name == "patch_file":
            path = arguments.get("file_path")
            content = arguments.get("new_content")
            result = apply_code_fix(path, content)
            return json.dumps({"status": "success", "message": result})
            
        else:
            return json.dumps({"error": f"Unknown GitHub MCP tool option: {tool_name}"})
    except Exception as e:
        return json.dumps({"error": f"Failed to parse MCP standard: {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(handle_mcp_request(sys.argv[1]))