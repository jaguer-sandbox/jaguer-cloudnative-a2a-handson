from google.adk import Agent

root_agent = Agent(
    name="command_center_agent",
    model="gemini-2.5-flash",
    description="""
    ミッションを開始する司令部.
    スタートという文言を受けたら動きます.
    """,
    instruction="""
    ゲームの説明を行います.
    その後 keymaster_agent へ遷移を促します.
    """
)
