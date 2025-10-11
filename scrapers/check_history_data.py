#!/usr/bin/env python3
import json

with open('all_princeton_academic_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total events: {len(data["events"])}')

# Check what departments are actually in the data
departments = set()
for event in data['events'][:50]:  # Check first 50 events
    dept = event.get('department', 'Unknown')
    departments.add(dept)

print(f'\nDepartments found: {sorted(departments)}')

print('\nFirst few events:')
for i, event in enumerate(data['events'][:5]):
    print(f'\nEvent {i+1}:')
    print(f'  Title: {event.get("title", "NULL")}')
    print(f'  Department: {event.get("department", "NULL")}')
    print(f'  Description: {event.get("description", "NULL")[:50]}...')
    print(f'  Date: {event.get("start_date", "NULL")}')
    print(f'  Location: {event.get("location", "NULL")}')
    print(f'  Has description: {bool(event.get("description"))}')
    print(f'  Has date: {bool(event.get("start_date"))}')
    print(f'  Has location: {bool(event.get("location"))}')

# Look for History events specifically
history_events = [e for e in data['events'] if e.get('department') == 'History']
print(f'\nHistory events found: {len(history_events)}')
if history_events:
    print('\nFirst History event:')
    for key, value in history_events[0].items():
        if value or value == []:
            print(f'  {key}: {value}')
