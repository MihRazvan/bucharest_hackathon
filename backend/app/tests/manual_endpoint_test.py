# app/tests/manual_endpoint_test.py
import httpx
import asyncio
import json

async def test_endpoints():
    """Test the API endpoints manually"""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Test the rate agent endpoints
        print("\n--- Testing Rate Agent Endpoints ---")
        response = await client.get("/api/rates/recommend")
        print(f"Recommended Rates Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        
        # Test the trading agent endpoints
        print("\n--- Testing Trading Agent Endpoints ---")
        # Generate a trading plan
        response = await client.post("/api/trading/plan", json={"idle_funds_amount": 1.5})
        print(f"Generate Trading Plan Response: {response.status_code}")
        plan_id = None
        if response.status_code == 200:
            data = response.json()
            plan_id = data.get("plan_id")
            print(f"Plan ID: {plan_id}")
            print(json.dumps(data["parsed_plan"], indent=2))
        
        # Execute the trading plan if available
        if plan_id:
            print("\n--- Executing Trading Plan ---")
            response = await client.post(f"/api/trading/execute/{plan_id}")
            print(f"Execute Trading Plan Response: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=2))
        
        # Get active positions
        print("\n--- Getting Active Positions ---")
        response = await client.get("/api/trading/positions")
        print(f"Active Positions Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        
        # Get trade history
        print("\n--- Getting Trade History ---")
        response = await client.get("/api/trading/history")
        print(f"Trade History Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(test_endpoints())