"""NBLM — Agent Loop (Component 1 of 9)."""
import json
from backend.harness.context import ContextManager
from backend.harness.tools import ToolRegistry
from backend.harness.permissions import check_permission
from backend.services.api_rotator import call_llm

MAX_ITERATIONS = 20

class AgentLoop:
    def __init__(self, db):
        self.db = db
        self.ctx = ContextManager(db)
        self.tools = ToolRegistry(db)

    async def run(self, user_msg: str, history: list = None) -> dict:
        messages = await self.ctx.build_messages(user_msg, history)
        tool_defs = [{"type":"function","function":{"name":n,"description":f"Tool: {n}"}} for n in self.tools.tool_names]
        for i in range(MAX_ITERATIONS):
            result = await call_llm(self.db, messages, tools=tool_defs)
            content = result.get("content","")
            tc = result.get("tool_calls")
            if not tc:
                return {"answer": content, "model_used": result.get("model_used"), "provider_used": result.get("provider_used")}
            messages.append({"role":"assistant","content":content,"tool_calls":tc})
            for call in tc:
                fn = call.get("function",{})
                name = fn.get("name","")
                args = json.loads(fn.get("arguments","{}")) if isinstance(fn.get("arguments"),str) else fn.get("arguments",{})
                if check_permission(name, args):
                    out = await self.tools.execute(name, args)
                else:
                    out = {"error":"Permission denied"}
                messages.append({"role":"tool","tool_call_id":call.get("id",""),"content":json.dumps(out,ensure_ascii=False)})
        return {"answer":"Đã vượt quá số bước tối đa.","model_used":None}
