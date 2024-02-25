from __future__ import print_function
from AppKit import NSWorkspace  # Use 'AppKit' with capital 'K'
import time
from Foundation import *
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re  # Add this line to import the 're' module

# Global dictionary to store timers for different windows and tabs
window_timers = {}

# Function to extract the base URL
def get_base_url(url):
    if url:
        match = re.match(r'(https?://[^/]+)', url)
        return match.group(1) if match else url
    return url

# Function to start the timer for a specific window and tab
def start_timer(window_name, tab_id):
    window_timers[window_name] = {'start_time': datetime.now(), 'tabs': {tab_id: {'start_time': datetime.now()}}}

# Function to stop the timer for a specific window, tab, and record the time in a JSON file
def stop_timer(window_name, tab_id, json_file):
    start_time = window_timers.get(window_name, {}).get('tabs', {}).get(tab_id, {}).get('start_time')

    if start_time is not None:
        end_time = datetime.now()
        elapsed_time = end_time - start_time

        # Load existing JSON data or create an empty dictionary
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Calculate elapsed time in hours, minutes, and seconds
        elapsed_hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
        elapsed_minutes, elapsed_seconds = divmod(remainder, 60)

        # Extract the base URL using regular expression
        base_url = get_base_url(window_timers[window_name].get('tabs', {}).get(tab_id, {}).get('active_tab_url'))

        # Add or update the elapsed time and base URL in the data
        window_data = {
            'start_time': start_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'elapsed_time_hours': int(elapsed_hours),
            'elapsed_time_minutes': int(elapsed_minutes),
            'elapsed_time_seconds': int(elapsed_seconds),
            'active_tab_url': base_url
        }

        # Add or update the window data in the JSON file
        data.setdefault(window_name, {}).setdefault('tabs', {}).setdefault(tab_id, {}).update(window_data)

        # Write the updated data back to the JSON file
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=2, default=str)

# Main loop
active_window_name = ""
active_tab_id = "default_tab"  # Default tab ID
json_file_path = "timer_data.json"

while True:
    new_window_name = (NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName'])

    if active_window_name != new_window_name:
        # Stop the timer for the previous window and record the time
        if active_window_name:
            stop_timer(active_window_name, active_tab_id, json_file_path)

        # Start the timer for the new window and default tab
        active_window_name = new_window_name
        active_tab_id = "default_tab"
        start_timer(active_window_name, active_tab_id)

        print(active_window_name)

    # Additional check for 'Brave Browser' to detect new tabs
    if active_window_name == 'Brave Browser':
        textOfMyScript = """tell app "Brave Browser" to get the url of the active tab of window 1"""
        s = NSAppleScript.initWithSource_(NSAppleScript.alloc(), textOfMyScript)
        results, err = s.executeAndReturnError_(None)
        current_tab_url = results.stringValue()

        if current_tab_url != active_tab_id:
            # Stop the timer for the previous tab and record the time
            stop_timer(active_window_name, active_tab_id, json_file_path)

            # Start the timer for the new tab
            active_tab_id = current_tab_url
            start_timer(active_window_name, active_tab_id)
            print(f"New tab URL: {current_tab_url}")

    time.sleep(10)
