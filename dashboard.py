import time

import requests
import urllib3

# Disable SSL warnings (only for testing purposes)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Splunk REST API endpoints
BASE_URL = "https://127.0.0.1:8089/servicesNS/admin/search/data/ui/views"
DASHBOARD_NAME = "automated_dashboard_1"
CREATE_DASHBOARD_URL = BASE_URL
REFRESH_VIEWS_URL = (
    "https://127.0.0.1:8089/servicesNS/admin/search/data/ui/views/_reload"
)
SET_PERMISSIONS_URL = f"{BASE_URL}/{DASHBOARD_NAME}/acl"

# Splunk credentials
SPLUNK_USERNAME = "admin"
SPLUNK_PASSWORD = "splunkent"

# Dashboard XML content
dashboard_data = """
<form version="1.1">
  <label>Automated Dashboard</label>
  <description>Dashboard created or updated via API with multiple panels</description>
  <fieldset submitButton="false" autoRun="true">
    <input type="time" token="global_time_picker" searchWhenChanged="true">
      <label>Global Time Range</label>
      <default>
        <earliest>-24h@h</earliest>
        <latest>now</latest>
      </default>
    </input>
  </fieldset>
  <row>
    <panel>
      <title>Total Events (API Calls)</title>
      <single>
        <search>
          <query>index="crud_index" | stats count as "Total Events"</query>
          <earliest>$global_time_picker.earliest$</earliest>
          <latest>$global_time_picker.latest$</latest>
        </search>
        <option name="drilldown">all</option>
        <option name="refresh.display">progressbar</option>
      </single>
    </panel>
    <panel>
      <title>Total Errors</title>
      <single>
        <search>
          <query>index="crud_index" response_code&gt;=400 | stats count as "Total Errors"</query>
          <earliest>$global_time_picker.earliest$</earliest>
          <latest>$global_time_picker.latest$</latest>
        </search>
        <option name="drilldown">all</option>
        <option name="refresh.display">progressbar</option>
      </single>
    </panel>
  </row>
  <row>
    <panel>
      <title>Response Code Distribution</title>
      <chart>
        <search>
          <query>index="crud_index" | stats count by response_code | rename response_code as "Response Code", count as "Event Count"</query>
          <earliest>$global_time_picker.earliest$</earliest>
          <latest>$global_time_picker.latest$</latest>
        </search>
        <option name="charting.chart">pie</option>
        <option name="charting.drilldown">all</option>
        <option name="refresh.display">progressbar</option>
      </chart>
    </panel>
  </row>
  <row>
    <panel>
      <title>Event Count (Sorted)</title>
      <chart>
        <search>
          <query>index="crud_index" | stats count by response_code | sort -count</query>
          <earliest>$global_time_picker.earliest$</earliest>
          <latest>$global_time_picker.latest$</latest>
        </search>
        <option name="charting.chart">column</option>
        <option name="charting.drilldown">all</option>
        <option name="refresh.display">progressbar</option>
      </chart>
    </panel>
  </row>
  <row>
    <panel>
      <title>API Event Table</title>
      <table>
        <search>
          <query>index="crud_index" | table index, API_message, username, response_code</query>
          <earliest>$global_time_picker.earliest$</earliest>
          <latest>$global_time_picker.latest$</latest>
        </search>
        <option name="drilldown">cell</option>
        <option name="refresh.display">progressbar</option>
      </table>
    </panel>
  </row>
</form>
"""

# HTTP headers
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
}


def dashboard_exists(dashboard_name):
    """Check if the dashboard exists by name."""
    try:
        response = requests.get(
            f"{BASE_URL}/{dashboard_name}",
            auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
            verify=False,
        )
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error checking dashboard existence: {e}")
        return False


def refresh_views():
    """Refresh Splunk's view cache to recognize newly created dashboards."""
    try:
        response = requests.get(
            REFRESH_VIEWS_URL,
            auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
            verify=False,
        )
        if response.status_code in [200, 201]:
            print("Views cache reloaded successfully.")
        else:
            print(f"Failed to reload views: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing views: {e}")


def set_dashboard_permissions(dashboard_name):
    """Set permissions for the specified dashboard."""
    permissions_payload = {
        "sharing": "app",
        "owner": "admin",
        "perms.read": "user,admin",
        "perms.write": "admin",
    }

    try:
        response = requests.post(
            f"{BASE_URL}/{dashboard_name}/acl",
            auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
            headers=HEADERS,
            data=permissions_payload,
            verify=False,
        )
        if response.status_code in [200, 201]:
            print(f"Permissions set successfully for '{dashboard_name}'.")
        else:
            print(
                f"Failed to set permissions: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error setting permissions: {e}")


def create_dashboard(dashboard_name, dashboard_xml):
    """Create the dashboard if it does not exist."""
    payload = {"name": dashboard_name, "eai:data": dashboard_xml}
    try:
        response = requests.post(
            CREATE_DASHBOARD_URL,
            auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
            headers=HEADERS,
            data=payload,
            verify=False,
        )
        if response.status_code in [200, 201]:
            print(f"Dashboard '{dashboard_name}' created successfully.")
            return True
        else:
            print(
                f"Failed to create dashboard: {response.status_code} - {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error during dashboard creation: {e}")
        return False


def update_dashboard(dashboard_name, dashboard_xml):
    """Attempt to update the dashboard, retrying if necessary."""
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            response = requests.post(
                f"{BASE_URL}/{dashboard_name}",
                auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
                headers=HEADERS,
                data={"eai:data": dashboard_xml},
                verify=False,
            )
            if response.status_code in [200, 201]:
                print(f"Dashboard '{dashboard_name}' updated successfully.")
                return True
            else:
                print(
                    f"Update attempt {retry_count + 1} failed: {response.status_code} - {response.text}"
                )
                retry_count += 1
                time.sleep(5)  # Wait 5 seconds before retrying
        except requests.exceptions.RequestException as e:
            print(f"Error during dashboard update: {e}")
            retry_count += 1
            time.sleep(5)

    print(f"Failed to update '{dashboard_name}' after multiple attempts.")
    return False


def create_or_update_dashboard(dashboard_name, dashboard_xml):
    """Manage the creation or update of the dashboard."""
    if dashboard_exists(dashboard_name):
        # Attempt to update if the dashboard exists
        if not update_dashboard(dashboard_name, dashboard_xml):
            print(
                "Update failed. Consider checking dashboard access or network status."
            )
    else:
        # If the dashboard does not exist, create it
        if create_dashboard(dashboard_name, dashboard_xml):
            # Wait and confirm the dashboard exists after creation
            time.sleep(10)  # Initial wait to allow creation to propagate
            retry_count = 0
            max_retries = 5
            while retry_count < max_retries:
                if dashboard_exists(dashboard_name):
                    print(f"Dashboard '{dashboard_name}' is now accessible.")
                    break
                time.sleep(5)
                retry_count += 1

            if retry_count == max_retries:
                print("Dashboard is not accessible after creation.")

            # Refresh the view cache to ensure the dashboard is registered
            refresh_views()

            # Check again for accessibility after cache refresh
            if not dashboard_exists(dashboard_name):
                print("Dashboard is still not accessible after cache refresh.")

    # Set permissions after creation or update
    set_dashboard_permissions(dashboard_name)


# Execute the create or update logic
create_or_update_dashboard(DASHBOARD_NAME, dashboard_data)
