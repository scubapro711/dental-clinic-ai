import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def run_test_suite():
    """Comprehensive end-to-end test suite for the dental clinic AI system."""
    print("--- Starting Aggressive End-to-End Test Suite ---")

    async with httpx.AsyncClient() as client:
        # 1. Test Health and Status Endpoints
        try:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            print("✅ Health Check: PASSED")
        except Exception as e:
            print(f"❌ Health Check: FAILED - {e}")

        try:
            response = await client.get(f"{BASE_URL}/status")
            assert response.status_code == 200
            print("✅ Status Check: PASSED")
        except Exception as e:
            print(f"❌ Status Check: FAILED - {e}")

        # 2. Test AI Agent Processing
        try:
            response = await client.post(
                f"{BASE_URL}/api/process_message",
                json={"text": "שלום, אני רוצה לקבוע תור", "metadata": {}},
            )
            assert response.status_code == 200
            print("✅ AI Agent Processing: PASSED")
        except Exception as e:
            print(f"❌ AI Agent Processing: FAILED - {e}")

        # 3. Test Simulation Agent
        try:
            # Start simulation
            response = await client.post(
                f"{BASE_URL}/api/start_simulation",
                json={"duration_minutes": 1, "speed": 10},
            )
            assert response.status_code == 200
            assert response.json()["status"] == "simulation_started"
            print("✅ Simulation Start: PASSED")

            # Wait for simulation to run
            await asyncio.sleep(5)

            # Check simulation status
            response = await client.get(f"{BASE_URL}/api/simulation_status")
            assert response.status_code == 200
            print("✅ Simulation Status Check: PASSED")

        except Exception as e:
            print(f"❌ Simulation Agent: FAILED - {e}")

    print("--- Test Suite Finished ---")

if __name__ == "__main__":
    asyncio.run(run_test_suite())
