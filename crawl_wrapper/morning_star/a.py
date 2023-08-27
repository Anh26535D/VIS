import json

with open('edge-net-export-log.json') as f:
    log_entries = json.load(f)

def check_bearer_token(log_entry):
    if "params" in log_entry and "headers" in log_entry["params"]:
        headers = log_entry["params"]["headers"]
        return "Authorization: Bearer" in headers
    return False

event_entries = log_entries["events"]

for entry in event_entries:
    if check_bearer_token(entry):
        print(entry["params"]["headers"].split("\r\n")[0])
        break