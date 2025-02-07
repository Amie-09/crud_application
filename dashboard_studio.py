import json

import boto3
import requests
import urllib3

# Disable SSL warnings (for testing purposes only; ensure to use SSL in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# AWS Secrets Manager details
secret_name = "token"

# Splunk REST API details
BASE_URL = "https://127.0.0.1:8089/servicesNS/Nobody/search/data/ui/views"
DASHBOARD_NAME = "automated_dashboard_studio"
DASHBOARD_URL = f"{BASE_URL}/{DASHBOARD_NAME}"
CREATE_DASHBOARD_URL = BASE_URL
ACL_URL = f"https://127.0.0.1:8089/servicesNS/Nobody/data/ui/views/{DASHBOARD_NAME}/acl"

# HTTP headers
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

# Define your Studio Dashboard JSON
dashboard_json = {
    "dataSources": {
        "ds_1nupyefH": {
            "type": "ds.search",
            "options": {
                "query": "index=crud_index \n| table _time, index, API_message, username, response_code",
                "queryParameters": {
                    "earliest": "$global_time.earliest$",
                    "latest": "$global_time.latest$",
                },
                "enableSmartSources": True,
            },
            "name": "table",
        },
        "ds_DaeGvKSd": {
            "type": "ds.chain",
            "options": {"query": "| fieldsummary maxvals=10", "extend": "ds_1nupyefH"},
            "name": "Events 2 search",
        },
        "ds_ttPmqcs2": {
            "type": "ds.search",
            "options": {
                "query": 'index=crud_index | stats count as "Total Events"\r\n',
                "enableSmartSources": True,
            },
            "name": "total_events",
        },
        "ds_0xUZjZjH": {
            "type": "ds.search",
            "options": {
                "query": "index=crud_index response_code>=400 OR response_code>=404 OR response_code>=500| stats count by username\r\n",
                "enableSmartSources": True,
            },
            "name": "error_by_username",
        },
        "ds_Wn68zxwA": {
            "type": "ds.search",
            "options": {
                "query": "index=crud_index | stats count by response_code\r\n",
                "enableSmartSources": True,
            },
            "name": "response_code_count",
        },
        "ds_sEJkkcvU": {
            "type": "ds.search",
            "options": {
                "query": "index=crud_index | stats count by response_code\r\n",
                "enableSmartSources": True,
            },
            "name": "response_code",
        },
        "ds_i4TVoCNI": {
            "type": "ds.search",
            "options": {
                "query": 'index=crud_index response_code>=400 | stats count as "Total Error Count"\r\n',
                "enableSmartSources": True,
            },
            "name": "error_count",
        },
    },
    "visualizations": {
        "viz_3D3MYocz": {
            "type": "splunk.table",
            "dataSources": {"primary": "ds_1nupyefH"},
            "containerOptions": {},
            "showProgressBar": False,
            "showLastUpdated": False,
            "title": "API Information",
        },
        "viz_gjZ6bj64": {
            "type": "splunk.singlevalue",
            "dataSources": {"primary": "ds_ttPmqcs2"},
            "title": "Total Events",
        },
        "viz_sIUA0VO3": {
            "type": "splunk.pie",
            "options": {"showDonutHole": True},
            "dataSources": {"primary": "ds_0xUZjZjH"},
            "title": "Error by Username",
        },
        "viz_k4EafJqF": {
            "type": "splunk.pie",
            "dataSources": {"primary": "ds_Wn68zxwA"},
            "title": "Count by Response Code",
            "options": {
                "seriesColors": [
                    "#1a8929",
                    "#af1126",
                    "#0051B5",
                    "#008C80",
                    "#99B100",
                    "#FFA476",
                    "#FF6ACE",
                    "#AE8CFF",
                    "#00689D",
                    "#00490A",
                    "#465D00",
                    "#9D6300",
                    "#F6540B",
                    "#FF969E",
                    "#E47BFE",
                ]
            },
        },
        "viz_g7NmuMHe": {
            "type": "splunk.column",
            "dataSources": {"primary": "ds_sEJkkcvU"},
            "containerOptions": {},
            "showProgressBar": False,
            "showLastUpdated": False,
            "options": {
                "dataValuesDisplay": "minmax",
                "seriesColors": [
                    "#00a4fd",
                    "#00CDAF",
                    "#DD9900",
                    "#FF677B",
                    "#CB2196",
                    "#813193",
                    "#0051B5",
                    "#008C80",
                    "#99B100",
                    "#FFA476",
                    "#FF6ACE",
                    "#AE8CFF",
                    "#00689D",
                    "#00490A",
                    "#465D00",
                    "#9D6300",
                    "#F6540B",
                    "#FF969E",
                    "#E47BFE",
                ],
            },
            "title": "Status Chart",
        },
        "viz_JiufYHhw": {
            "type": "splunk.singlevalue",
            "dataSources": {"primary": "ds_i4TVoCNI"},
            "title": "Error Count",
        },
    },
    "inputs": {
        "input_global_trp": {
            "type": "input.timerange",
            "options": {"token": "global_time", "defaultValue": "-24h@h,now"},
            "title": "Global Time Range",
        }
    },
    "layout": {
        "type": "absolute",
        "options": {"width": 1440, "height": 960, "display": "auto"},
        "structure": [
            {
                "item": "viz_3D3MYocz",
                "type": "block",
                "position": {"x": 0, "y": 660, "w": 1440, "h": 300},
            },
            {
                "item": "viz_gjZ6bj64",
                "type": "block",
                "position": {"x": 0, "y": 0, "w": 440, "h": 330},
            },
            {
                "item": "viz_sIUA0VO3",
                "type": "block",
                "position": {"x": 440, "y": 0, "w": 1000, "h": 330},
            },
            {
                "item": "viz_k4EafJqF",
                "type": "block",
                "position": {"x": 0, "y": 330, "w": 540, "h": 330},
            },
            {
                "item": "viz_g7NmuMHe",
                "type": "block",
                "position": {"x": 540, "y": 330, "w": 480, "h": 330},
            },
            {
                "item": "viz_JiufYHhw",
                "type": "block",
                "position": {"x": 1020, "y": 330, "w": 420, "h": 330},
            },
        ],
        "globalInputs": ["input_global_trp"],
    },
    "title": "Python Automated Dashboard",
    "description": "",
    "defaults": {
        "dataSources": {
            "ds.search": {
                "options": {
                    "queryParameters": {
                        "latest": "$global_time.latest$",
                        "earliest": "$global_time.earliest$",
                    }
                }
            }
        }
    },
}


# Function to retrieve the token from AWS Secrets Manager
def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        secret = json.loads(response["SecretString"])
        return secret.get("token")
    else:
        raise Exception("Token not found in the secret.")


# Function to check if dashboard exists in Splunk
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

        # If the response status code is 200, the dashboard exists
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            # If the status code is 404, the dashboard does not exist
            return False
        else:
            print(
                f"Error checking dashboard existence: {response.status_code} - {response.text}"
            )
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error during dashboard existence check: {e}")
        return False


# Function to create a Dashboard Studio in Splunk
def create_dashboard(token):
    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }

    # Encode the data in the required format for eai:data
    payload = {
        "name": DASHBOARD_NAME,
        "eai:data": f'<dashboard version="2" theme="dark">'
        f'<label>{dashboard_json["title"]}</label>'
        f'<description>{dashboard_json["description"]}</description>'
        f'<definition><![CDATA[{json.dumps(dashboard_json)}]]></definition>'
        f'<meta type="hiddenElements"><![CDATA[{{"hideEdit": false, "hideOpenInSearch": false, "hideExport": false}}]]></meta>'
        f'</dashboard>',
    }

    try:
        response = requests.post(
            CREATE_DASHBOARD_URL, headers=headers, data=payload, verify=False
        )

        if response.status_code in [200, 201]:
            print(f"Dashboard '{DASHBOARD_NAME}' created successfully.")
        else:
            print(
                f"Failed to create dashboard: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error during dashboard creation: {e}")


# Function to update a Dashboard Studio in Splunk
def update_dashboard(token):
    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }

    # Prepare the payload correctly for an update
    payload = {
        "eai:data": f'<dashboard version="2" theme="dark">'
        f'<label>{dashboard_json["title"]}</label>'
        f'<description>{dashboard_json["description"]}</description>'
        f'<definition><![CDATA[{json.dumps(dashboard_json)}]]></definition>'
        f'<meta type="hiddenElements"><![CDATA[{{"hideEdit": false, "hideOpenInSearch": false, "hideExport": False}}]]></meta>'
        f'</dashboard>',
    }

    try:
        # Perform a POST request to the dashboard's endpoint
        response = requests.post(
            f"{BASE_URL}/{DASHBOARD_NAME}", headers=headers, data=payload, verify=False
        )

        if response.status_code in [200, 201]:
            print(f"Dashboard '{DASHBOARD_NAME}' updated successfully.")
        elif response.status_code == 409:
            print(
                f"Conflict occurred: Dashboard '{DASHBOARD_NAME}' might already exist."
            )
        else:
            print(
                f"Failed to update dashboard: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error during dashboard update: {e}")


# Function to set permissions to a Dashboard Studio in Splunk
def set_permissions(dashboard_name, token):
    """Set permissions for the specified dashboard."""
    # Define the permissions you want to set
    permissions_payload = {
        "sharing": "app",  # Options: "app", "user", "global"
        "owner": "splunk",  # Specify the owner
        "perms.read": "user,splunk",  # Users who can read the dashboard
        "perms.write": "splunk",  # Users who can write to the dashboard
    }

    headers = {
        "Authorization": f"Bearer {token}",
        **HEADERS,
    }

    try:
        # Send the permissions update request
        response = requests.post(
            f"{BASE_URL}/{dashboard_name}/acl",  # Endpoint to set permissions
            headers=headers,
            data=permissions_payload,  # Use JSON format for the payload
            verify=False,  # Consider setting this to True if possible
        )

        if response.status_code in [200, 201]:
            print(f"Permissions set successfully for '{dashboard_name}'.")
        else:
            print(
                f"Failed to set permissions: {response.status_code} - {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error setting permissions: {e}")


def main():
    try:
        token = get_secret(secret_name)
        if not token:
            raise Exception("Token not found in the secret.")

        if dashboard_exists(DASHBOARD_NAME, token):
            print(f"Dashboard '{DASHBOARD_NAME}' already exists. Updating...")
            update_dashboard(token)  # Call the updated function
        else:
            print(f"Dashboard '{DASHBOARD_NAME}' does not exist. Creating...")
            create_dashboard(token)  # Call your create function here

        # Set permissions after create/update
        set_permissions(DASHBOARD_NAME, token)

    except Exception as e:
        print(f"Error: {e}")


# Run the script
if __name__ == "__main__":
    main()




# changed False to false in the payload