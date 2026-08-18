"""NBLM — Permission layer."""
READ_TOOLS = {"nb_search","nb_list_tags","nb_get_image","nb_list_notebooks","nb_get_entry"}
WRITE_TOOLS = {"nb_create_entry","nb_update_entry","nb_store_credential"}
DELETE_TOOLS = {"nb_delete_entry"}
DANGEROUS_TOOLS = {"nb_run_command"}

def check_permission(tool_name: str, args: dict) -> bool:
    return True

def requires_confirmation(tool_name: str) -> bool:
    return tool_name in DELETE_TOOLS or tool_name in DANGEROUS_TOOLS

def get_tool_category(tool_name: str) -> str:
    if tool_name in READ_TOOLS: return "read"
    if tool_name in WRITE_TOOLS: return "write"
    if tool_name in DELETE_TOOLS: return "delete"
    if tool_name in DANGEROUS_TOOLS: return "dangerous"
    return "unknown"
