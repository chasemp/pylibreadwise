import datetime
import requests  # This may need to be installed from pip
import pprint
import json
import yaml

import urllib3
urllib3.disable_warnings()

def read_value_from_yaml(file_path, key):
  """Reads a value from a YAML file.

  Args:
    file_path: The path to the YAML file.
    key: The key to retrieve the value for.

  Returns:
    The value associated with the key, or None if the key is not found
    or if there's an error parsing the YAML file.
  """
  with open(file_path, 'r') as f:
    data = yaml.safe_load(f)  # Use safe_load for security
  if isinstance(data, dict) and key in data:
    return data[key]
  return None

def fetch_reader_document_list_api(updated_after=None, location=None, content=True, token=None):
    full_data = []
    next_page_cursor = None
    while True:
        params = {}
        if next_page_cursor:
            params['pageCursor'] = next_page_cursor
        if updated_after:
            params['updatedAfter'] = updated_after
        if location:
            params['location'] = location
        if content:
            params['withHtmlContent'] = content

        print("Making export api request with params " + str(params) + "...")
        response = requests.get(
            url="https://readwise.io/api/v3/list/",
            params=params,
            headers={"Authorization": f"Token {token}"}, verify=False
        )
        try:
            full_data.extend(response.json()['results'])
        except KeyError:
            print(response.json()); exit()

        next_page_cursor = response.json().get('nextPageCursor')
        if not next_page_cursor:
            break
    return full_data

key = read_value_from_yaml('secret.yaml', 'token')

# Get all of a user's documents from all time
## all_data = fetch_reader_document_list_api(token=key)

# Get all of a user's archived documents
## archived_data = fetch_reader_document_list_api(location='archive', token=key)

# Later, if you want to get new documents updated after some date, do this:
docs_after_date = datetime.datetime.now() - datetime.timedelta(days=1)  # use your own stored date
new_data = fetch_reader_document_list_api(docs_after_date.isoformat(), token=key)

# print(new_data)
print(new_data[0])
