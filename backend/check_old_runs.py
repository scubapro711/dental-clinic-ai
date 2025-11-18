from langsmith import Client
from datetime import datetime, timedelta
import os

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

end_time = datetime.now()
start_time = end_time - timedelta(days=30)

print(f"Checking runs from {start_time.date()} to {end_time.date()}")
print()

runs = list(client.list_runs(
    project_name="dentaflow-agent-eval",
    start_time=start_time,
    end_time=end_time,
    limit=100
))

print(f"Total runs found: {len(runs)}")

if runs:
    print("\nFirst 10 runs:")
    for i, run in enumerate(runs[:10], 1):
        status = "✅" if not run.error else "❌"
        print(f"{i}. {status} {run.name} - {run.start_time}")
