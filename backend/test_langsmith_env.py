import os

# Set environment
# LANGSMITH_API_KEY should be set in environment variables
os.environ["LANGSMITH_PROJECT"] = "dentaflow-agent-eval"
os.environ["LANGSMITH_TRACING"] = "true"

print("Environment variables:")
print(f"LANGSMITH_API_KEY: {os.getenv('LANGSMITH_API_KEY')[:20]}...")
print(f"LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT')}")
print(f"LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING')}")
print()

from langsmith import Client, traceable

client = Client()
print(f"LangSmith Client initialized: {client}")
print()

@traceable(name="test_trace")
def test_function():
    return "Hello from traced function"

result = test_function()
print(f"Result: {result}")
print()
print("✅ If you see this, tracing is configured correctly!")
print("Check LangSmith UI for the trace.")
