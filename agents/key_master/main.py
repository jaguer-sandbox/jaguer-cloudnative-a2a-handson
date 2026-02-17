
import logging
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .agent import root_agent

logging.basicConfig(level=logging.INFO)

app = to_a2a(root_agent)
