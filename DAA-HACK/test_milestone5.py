"""Test Milestone 5 — Triage priority queue and API endpoints."""

import subprocess, sys, time, urllib.request, json

# Start the server
proc = subprocess.Popen(
    [sys.executable, '-m', 'uvicorn', 'backend.app.main:app',
     '--host', '127.0.0.1', '--port', '8000', '--reload'],
    cwd=r'C:\Users\NIMISHAMBIKA\OneDrive\Desktop\DAA-HACK',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(3)

try:
    results = []

    # Test 1: GET /graph
    try:
        r = urllib.request.urlopen('http://127.0.0.1:8000/graph', timeout=5)
        data = json.loads(r.read())
        results.append(f"GET /graph: Status {r.status}, Nodes {len(data['nodes'])}, Edges {len(data['edges'])}")
    except Exception as e:
        results.append(f"GET /graph Error: {e}")

    # Test 2: POST /call - Stroke Alert to N10
    try:
        req = urllib.request.Request(
            'http://127.0.0.1:8000/call',
            data=json.dumps({'type': 'Stroke Alert', 'dst': 'N10'}).encode(),
            headers={'Content-Type': 'application/json'}
        )
        r = urllib.request.urlopen(req, timeout=5)
        data = json.loads(r.read())
        call = data.get('call', {})
        queue_len = len(data.get('queue', []))
        results.append(f"POST /call: Success, queue len={queue_len}, call path={call.get('path')}, eta={call.get('eta')}")
    except Exception as e:
        results.append(f"POST /call Error: {e}")

    # Test 3: POST /call - Cardiac Arrest to N02
    try:
        req = urllib.request.Request(
            'http://127.0.0.1:8000/call',
            data=json.dumps({'type': 'Cardiac Arrest', 'dst': 'N02'}).encode(),
            headers={'Content-Type': 'application/json'}
        )
        r = urllib.request.urlopen(req, timeout=5)
        data = json.loads(r.read())
        results.append(f"POST /call (Cardiac Arrest): queue len={len(data.get('queue', []))}")
    except Exception as e:
        results.append(f"POST /call (Cardiac Arrest) Error: {e}")

    # Test 4: GET /queue
    try:
        r = urllib.request.urlopen('http://127.0.0.1:8000/queue', timeout=5)
        data = json.loads(r.read())
        queue = data.get('queue', [])
        results.append(f"GET /queue: {len(queue)} calls in queue")
        for c in queue[:3]:
            results.append(f"  - {c.get('id')[:8]}... -> {c.get('dst')}, ETA={c.get('eta')}, sev={c.get('severity')}")
    except Exception as e:
        results.append(f"GET /queue Error: {e}")

    # Print all results
    print("\n".join(results))

finally:
    proc.terminate()
    proc.wait(timeout=5)
    print("\nServer stopped. Milestone 5 tests completed.")