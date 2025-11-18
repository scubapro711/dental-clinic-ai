from langsmith import Client
from datetime import datetime, timedelta
import os

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Check last 10 minutes
end_time = datetime.now()
start_time = end_time - timedelta(minutes=10)

print(f"Checking traces from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
print()

runs = list(client.list_runs(
    project_name="dentaflow-agent-eval",
    start_time=start_time,
    end_time=end_time,
    limit=50
))

print(f"✅ Found {len(runs)} traces!")
print()

if runs:
    print("Recent traces:")
    for i, run in enumerate(runs[:10], 1):
        status = "✅" if not run.error else "❌"
        duration = (run.end_time - run.start_time).total_seconds() if run.end_time and run.start_time else 0
        print(f"{i}. {status} {run.name} - {duration:.2f}s")
        if run.error:
            print(f"   Error: {str(run.error)[:100]}")
