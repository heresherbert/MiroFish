import requests
import time
import json

base_url = "http://localhost:5001/api"

print("0. Waiting for backend to be ready...")
for i in range(60):
    try:
        requests.get("http://localhost:5001/")
        print(f"Backend ready after {i} seconds!")
        break
    except Exception:
        time.sleep(1)

print("1. Generating ontology...")
with open("/Users/madafaka/Desktop/SimplyFire/Dev/mirofish/fart_post.txt", "rb") as f:
    files = {"files": ("fart_post.txt", f)}
    data = {
        "simulation_requirement": "Predict how my friends react on social media to me posting 'I farted'", 
        "project_name": "Fart Post Test"
    }
    res = requests.post(f"{base_url}/graph/ontology/generate", files=files, data=data).json()

print(json.dumps(res, indent=2))
project_id = res.get("data", {}).get("project_id") or res.get("project_id")
task_id = res.get("data", {}).get("task_id") or res.get("task_id")

if task_id:
    print(f"Ontology Task ID: {task_id}")
    while True:
        status = requests.get(f"{base_url}/graph/task/{task_id}").json()
        state = status.get("data", {}).get("status", "unknown")
        print("Ontology status:", state)
        if state in ["completed", "failed", "error"]:
            break
        time.sleep(3)
        
print("1a. Extracted Ontology!")

print("2. Building graph...")
res = requests.post(f"{base_url}/graph/build", json={"project_id": project_id, "graph_name": "fart_graph"}).json()
print(json.dumps(res, indent=2))
task_id = res.get("data", {}).get("task_id")
while True:
    status = requests.get(f"{base_url}/graph/task/{task_id}").json()
    state = status.get("data", {}).get("status", "unknown")
    print("Graph status:", state)
    if state in ["completed", "failed", "error"]:
        break
    time.sleep(3)

print("3. Creating simulation...")
res = requests.post(f"{base_url}/simulation/create", json={"project_id": project_id, "enable_twitter": True, "enable_reddit": False}).json()
print(json.dumps(res, indent=2))
sim_id = res.get("data", {}).get("simulation_id")

# Config patching moved to after preparation step

print("4. Preparing simulation...")
prep_res = requests.post(f"{base_url}/simulation/prepare", json={"simulation_id": sim_id, "parallel_profile_count": 2}).json()
prep_task_id = prep_res.get("data", {}).get("task_id")

while True:
    payload = {"simulation_id": sim_id}
    if prep_task_id:
        payload["task_id"] = prep_task_id
    status = requests.post(f"{base_url}/simulation/prepare/status", json=payload).json()
    state = status.get("data", {}).get("status", "unknown")
    print("Prepare status:", state)
    if state in ["completed", "ready"]:
        break
    elif state in ["failed", "error"]:
        print("Error during prepare:", status)
        import sys; sys.exit(1)
    time.sleep(3)

print("3a. Patching simulation config for 24/7 activity...")
import os
config_path = os.path.join(os.path.dirname(__file__), f"backend/uploads/simulations/{sim_id}/simulation_config.json")

if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    for agent in config.get("agent_configs", []):
        agent["active_hours"] = list(range(24))
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("Patched simulation_config.json for active hours!")
else:
    print(f"Warning: could not find config at {config_path} even after prepare!")

print("5. Starting simulation...")
res = requests.post(f"{base_url}/simulation/start", json={"simulation_id": sim_id, "max_rounds": 12, "platform": "twitter"}).json()
start_task_id = res.get("data", {}).get("task_id")
if start_task_id:
    while True:
        status = requests.get(f"{base_url}/task/{start_task_id}").json()
        state = status.get("data", {}).get("status", "unknown")
        print("Run Task Status:", state)
        if state in ["completed", "failed", "error"]:
            break
        time.sleep(3)
else:
    while True:
        status = requests.get(f"{base_url}/simulation/{sim_id}/run-status").json()
        data = status.get("data", {})
        state = data.get("runner_status", "unknown")
        print(f"Run status: {state} | Round: {data.get('current_round', 0)}")
        if state in ["completed", "idle", "failed", "error"] and data.get('current_round', 0) > 0:
            break
        elif state in ["failed", "error"]:
            break
        time.sleep(5)

print("\n=== FINAL RESULTS ===")
posts = requests.get(f"{base_url}/simulation/{sim_id}/posts?platform=twitter&limit=20").json()
for post in posts.get("data", {}).get("posts", []):
    print(f"[{post.get('author')}] {post.get('content')}")
