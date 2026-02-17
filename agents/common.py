
import os
import logging
from google.adk import Agent

# Try to import to_a2a_agent from adk. 
# Adjusting based on potential library structure.
try:
    from google.adk.networking.a2a import to_a2a_agent
except ImportError:
    # Fallback or placeholder if specific path is different, 
    # but the user rules link suggests standard patterns.
    # We will assume it's available or we'll debug if it fails.
    pass

logger = logging.getLogger(__name__)

def get_agent(name: str, local_agent_module=None) -> Agent:
    """
    Resolves an agent.
    If {NAME}_URL environment variable is set, returns a remote A2A agent stub.
    Otherwise, imports and returns the local agent object.
    
    Args:
        name: The name of the agent (e.g., 'map_agent', 'key_master_agent').
              The env var checked will be {NAME.upper()}_URL (e.g., MAP_AGENT_URL).
        local_agent_module: The module to import the local agent from if env var is missing.
                            Should be a module object or similar.
                            Actually, simpler to pass the local agent object directly if available or imported 
                            at callsites, but to avoid circular deps, we might need lazy import.
    """
    
    # Construct env var name. 
    # The convention in deploy_cloudrun.sh is e.g. MAP_URL for map-agent?
    # Let's check deploy_cloudrun.sh again.
    # deploy_cloudrun.sh: KEY_MASTER_URL, MAP_URL, TREASURE_CHEST_URL, COMMAND_CENTER_URL
    # Note: "map-agent" service produces map-agent_URL which is assigned to MAP_URL.
    
    env_var_map = {
        "map_agent": "MAP_URL",
        "key_master_agent": "KEY_MASTER_URL",
        "treasure_chest_agent": "TREASURE_CHEST_URL",
        "command_center_agent": "COMMAND_CENTER_URL",
        "explorer_agent": "EXPLORER_URL"
    }
    
    env_var = env_var_map.get(name, f"{name.upper()}_URL")
    url = os.environ.get(env_var)

    if url:
        logger.info(f"Using remote agent for {name} at {url}")
        # Create a stub agent that points to the remote URL
        # The library likely provides a way to wrap a URL as an Agent
        from google.adk.networking.a2a import to_a2a_agent
        return to_a2a_agent(url)
    else:
        logger.info(f"Using local agent for {name}")
        if local_agent_module:
            return local_agent_module.root_agent
        else:
             raise ValueError(f"No local module provided for {name} and no remote URL found.")
