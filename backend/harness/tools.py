"""NBLM — Tool Registry (Component 4 of 9)."""
import json, subprocess
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models import Entry, StoredCredential, Notebook

class ToolRegistry:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._tools = {
            "nb_search": self._search,
            "nb_create_entry": self._create_entry,
            "nb_update_entry": self._update_entry,
            "nb_delete_entry": self._delete_entry,
            "nb_list_tags": self._list_tags,
            "nb_get_image": self._get_image,
            "nb_run_command": self._run_command,
            "nb_store_credential": self._store_credential,
            "nb_list_notebooks": self._list_notebooks,
            "nb_get_entry": self._get_entry,
        }

    @property
    def tool_names(self): return list(self._tools.keys())

    async def execute(self, name: str, args: dict) -> dict:
        fn = self._tools.get(name)
        if not fn: return {"error": f"Unknown tool: {name}"}
        try: return await fn(args)
        except Exception as e: return {"error": str(e)}

    async def _search(self, args: dict) -> dict:
        q = args.get("query", "")
        limit = min(int(args.get("limit", 10)), 50)
        stmt = select(Entry).where(
            text("title ilike :q or blocks::text ilike :q")
        ).params(q=f"%{q}%").limit(limit)
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return {"count": len(rows), "entries": [
            {"id": r.id, "title": r.title, "tags": r.tags or [], "blocks_preview": str(r.blocks)[:200]}
            for r in rows
        ]}

    async def _create_entry(self, args: dict) -> dict:
        nb_id = args.get("notebook_id")
        title = args.get("title", "Untitled")
        blocks = args.get("blocks", [])
        tags = args.get("tags", [])
        entry = Entry(notebook_id=nb_id, title=title, blocks=blocks, tags=tags)
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return {"id": entry.id, "title": entry.title}

    async def _update_entry(self, args: dict) -> dict:
        eid = args.get("entry_id")
        entry = await self.db.get(Entry, eid)
        if not entry: return {"error": "Not found"}
        if "title" in args: entry.title = args["title"]
        if "blocks" in args: entry.blocks = args["blocks"]
        if "tags" in args: entry.tags = args["tags"]
        await self.db.commit()
        return {"id": entry.id, "updated": True}

    async def _delete_entry(self, args: dict) -> dict:
        eid = args.get("entry_id")
        entry = await self.db.get(Entry, eid)
        if not entry: return {"error": "Not found"}
        await self.db.delete(entry)
        await self.db.commit()
        return {"deleted": eid}

    async def _list_tags(self, args: dict) -> dict:
        stmt = text("select distinct unnest(tags) as tag from entries order by tag")
        result = await self.db.execute(stmt)
        return {"tags": [r[0] for r in result.fetchall()]}

    async def _get_image(self, args: dict) -> dict:
        return {"info": "Image retrieval via R2 presigned URL", "r2_key": args.get("r2_key")}

    async def _run_command(self, args: dict) -> dict:
        cmd = args.get("command", "")
        whitelist = ["ls", "pwd", "date", "echo", "cat", "head", "tail", "wc", "df", "free", "git status", "git log"]
        if not any(cmd.startswith(w) for w in whitelist):
            return {"error": f"Command not in whitelist: {cmd}"}
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return {"stdout": out.stdout[:2000], "stderr": out.stderr[:500], "exit_code": out.returncode}
        except Exception as e: return {"error": str(e)}

    async def _store_credential(self, args: dict) -> dict:
        from backend.services.crypto import encrypt_value
        label = args.get("label", "unnamed")
        value = args.get("value", "")
        enc = encrypt_value(value)
        cred = StoredCredential(label=label, category=args.get("category","api_key"), encrypted_value=enc["encrypted"], iv=enc["iv"])
        self.db.add(cred)
        await self.db.commit()
        return {"id": cred.id, "label": label}

    async def _list_notebooks(self, args: dict) -> dict:
        result = await self.db.execute(select(Notebook).order_by(Notebook.sort_order))
        nbs = result.scalars().all()
        return {"notebooks": [{"id": n.id, "name": n.name, "icon": n.icon} for n in nbs]}

    async def _get_entry(self, args: dict) -> dict:
        entry = await self.db.get(Entry, args.get("entry_id"))
        if not entry: return {"error": "Not found"}
        return {"id": entry.id, "title": entry.title, "blocks": entry.blocks, "tags": entry.tags or []}
