
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Cortex Calendar", port=8001)

@mcp.tool()
def generate_schedule(subjects: str, num_days: int) -> str:
    """Generate a day-by-day study schedule by distributing a comma-separated list of subjects/topics across a given number of days."""
    topic_list = [t.strip() for t in subjects.split(",") if t.strip()]

    if not topic_list:
        return "No subjects provided."

    schedule = {i: [] for i in range(1, num_days + 1)}
    for idx, topic in enumerate(topic_list):
        day = (idx % num_days) + 1
        schedule[day].append(topic)

    lines = []
    for day in range(1, num_days + 1):
        topics_today = schedule[day]
        if topics_today:
            lines.append(f"Day {day}: {', '.join(topics_today)}")
        else:
            lines.append(f"Day {day}: Review / buffer day")

    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run(transport="sse")
