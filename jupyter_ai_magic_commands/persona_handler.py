""" 
persona_handler call REST API in persona manager to get chat
result
"""
import json
import requests
from jupyter_server.serverapp import list_running_servers
from .parsers import CellArgs


def handle_persona(args: CellArgs, prompt: str) -> str:
    """
    Handle persona requests by calling a REST API via Jupyter Server.

    Args:
        model_id: The model ID containing @persona tag (e.g., "gpt-4@my-persona")
        prompt: The user's prompt/message to process

    Returns:
        The response from the persona API
    """
    persona_name = args.model_id.split("@")[-1]
    metadata = json.loads(args.model_parameters)
    last_error = None
    for server in list_running_servers():
        if 'base_url' not in server:
            continue

        api_url = f"{server['url']}api/ai/message/{persona_name}"
        session = requests.Session()
        try:
            session.verify = server.get("verify", True)
            headers = {}
            if token := server.get("token"):
                headers["Authorization"] = f"token {token}"
            if xsrf_token := server.get("cookie", {}).get("_xsrf"):
                headers["X-XSRF-Token"] = xsrf_token
            response = session.post(
                api_url, json={"message": prompt,
                               "metadata": metadata}, headers=headers
            )
            response.raise_for_status()
            return response.json().get("response", response.text)
        except Exception as e:
            last_error = e
            continue

    return f"Error calling persona API: {last_error}" \
        if last_error else "Error: No valid Jupyter Server instances found."
