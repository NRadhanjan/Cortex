
import os
import requests
from mcp.server.fastmcp import FastMCP

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = "NRadhanjan"

MY_REPOS = [
    "Cortex",
    "VisioCap",
    "DocuSense",
    "NeuroDetect",
    "PCOS-detection",
    "A-Minimalistic-Approach-to-Real-Time-Audio-Steganography-Using-Pseudo-Random-Sample-Embedding",
]

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

mcp = FastMCP("Cortex GitHub", port=8002)

@mcp.tool()
def list_my_projects() -> str:
    """List the user's key GitHub projects/repositories with short descriptions."""
    lines = []
    for repo in MY_REPOS:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            desc = data.get("description") or "No description"
            lang = data.get("language") or "Unknown"
            lines.append(f"- {repo} ({lang}): {desc}")
        else:
            lines.append(f"- {repo}: [could not fetch, status {resp.status_code}]")
    return "\n".join(lines)

@mcp.tool()
def get_project_readme(repo_name: str) -> str:
    """Get the README content of a specific project by repo name."""
    if repo_name not in MY_REPOS:
        return f"'{repo_name}' is not in the known project list. Available: {', '.join(MY_REPOS)}"

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/readme"
    resp = requests.get(url, headers={**HEADERS, "Accept": "application/vnd.github.raw+json"})
    if resp.status_code == 200:
        return resp.text[:4000]  # cap length to keep context manageable
    else:
        return f"Could not fetch README for {repo_name} (status {resp.status_code})"

if __name__ == "__main__":
    mcp.run(transport="sse")
