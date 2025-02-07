import json
import time

import boto3
import requests
import urllib3

# Disable SSL warnings (only for testing purposes)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# AWS Secrets Manager details
secret_name = "token"

# Splunk REST API endpoints
BASE_URL = "https://127.0.0.1:8089/servicesNS/Nobody/search/data/ui/views"
DASHBOARD_NAME = "automated_dashboard_token"
CREATE_DASHBOARD_URL = BASE_URL
SET_PERMISSIONS_URL = f"{BASE_URL}/{DASHBOARD_NAME}/acl"

# HTTP headers
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

# Dashboard XML content
dashboard_data = """
<form version="1.1">
  <label>Automated Dashboard using Token</label>
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
      <title>API Events Table</title>
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


def get_secret(secret_name):
    """Retrieve token from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        secret = json.loads(response["SecretString"])
        return secret.get("token")
    else:
        raise Exception("Secret not found.")


def dashboard_exists(dashboard_name, token):
    """Check if the dashboard exists by name."""
    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }
    try:
        response = requests.get(
            f"{BASE_URL}/{dashboard_name}",
            headers=headers,
            verify=False,
        )
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error checking dashboard existence: {e}")
        return False


def set_dashboard_permissions(dashboard_name, token):
    """Set permissions for the specified dashboard."""
    permissions_payload = {
        "sharing": "app",
        "owner": "splunk",
        "perms.read": "user,splunk",
        "perms.write": "splunk",
    }
    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/{dashboard_name}/acl",
            headers=headers,
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


def create_dashboard(dashboard_name, dashboard_xml, token):
    """Create the dashboard if it does not exist."""
    payload = {"name": dashboard_name, "eai:data": dashboard_xml}
    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }
    try:
        response = requests.post(
            CREATE_DASHBOARD_URL,
            headers=headers,
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


def update_dashboard(dashboard_name, dashboard_xml, token):
    """Attempt to update the dashboard, retrying if necessary."""
    retry_count = 0
    max_retries = 5
    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }

    while retry_count < max_retries:
        try:
            response = requests.post(
                f"{BASE_URL}/{dashboard_name}",
                headers=headers,
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


def create_or_update_dashboard(dashboard_name, dashboard_xml, token):
    """Manage the creation or update of the dashboard."""
    if dashboard_exists(dashboard_name, token):
        # Attempt to update if the dashboard exists
        if not update_dashboard(dashboard_name, dashboard_xml, token):
            print(
                "Update failed. Consider checking dashboard access or network status."
            )
    else:
        # If the dashboard does not exist, create it
        if create_dashboard(dashboard_name, dashboard_xml, token):
            # Wait and confirm the dashboard exists after creation
            time.sleep(10)  # Initial wait to allow creation to propagate
            retry_count = 0
            max_retries = 5
            while retry_count < max_retries:
                if dashboard_exists(dashboard_name, token):
                    print(f"Dashboard '{dashboard_name}' is now accessible.")
                    break
                time.sleep(5)
                retry_count += 1

            if retry_count == max_retries:
                print("Dashboard is not accessible after creation.")

    # Set permissions after creation or update
    set_dashboard_permissions(dashboard_name, token)


# Execute the create or update logic
def main():
    try:
        token = get_secret(secret_name)
        if not token:
            raise Exception("Token not found in the secret.")

        create_or_update_dashboard(DASHBOARD_NAME, dashboard_data, token)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
