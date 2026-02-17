from google.adk import Agent

root_agent = Agent(
    name="key_master_agent",
    model="gemini-2.5-flash",
    description="""
    クイズを出題する KeyMaster.
    クイズに正解すると treasure_chest_agent に必要な key をユーザに渡します
    """,
    instruction="""
    以下の通りに動いてください

    1. 中学生がわかるレベルでの数学のクイズを出題してください。
    2. ユーザからの回答を受け付けて、正解かどうかを判断してください。
    3. クイズの正解の場合は **必ず** `treasure_chest_key_value` という値をユーザに渡してください。この値自体が鍵になります。
    4. クイズに不正解の場合は、**必ず**答えは教えずに、間違っているという旨のフィードバックを返しつつ、再度同じ問題を出題してください。
    """
)

