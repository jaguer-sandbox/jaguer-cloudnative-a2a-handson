from google.adk import Agent
from typing import Dict

def treasure_tool(key: str) -> Dict[str, str]:
    """key を検証する関数"""
    if key != "treasure_chest_key_value":
        return {"error": "invalid key", "treasure": ""}
    return {"error": "", "treasure": "congratulations!! you got a2a client skills!!"}

root_agent = Agent(
    name="treasure_chest_agent",
    model="gemini-2.5-flash",
    description="key を渡すと宝箱を開けて宝を渡す Agent です",
    instruction="""
    ユーザから渡された key を使って検証をし、問題なければ宝を渡す Agent です.
    出てきた宝は **必ず** ユーザにメッセージとして返却してください。
    key は 'treasure_tool' を使って検証してください。
    検証して問題ある場合は **絶対に** 宝を渡さないでください。
    """,
    tools=[treasure_tool]
)
