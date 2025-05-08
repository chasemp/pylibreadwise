import yaml
from google import genai
from google.genai import types
import datetime
import requests  # This may need to be installed from pip

import urllib3
# https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
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

        ## print("Making export api request with params " + str(params) + "...")
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

gkey = read_value_from_yaml('secret.yaml', 'galf')
rkey = read_value_from_yaml('secret.yaml', 'token')

# Later, if you want to get new documents updated after some date, do this:
## docs_after_date = datetime.datetime.now() - datetime.timedelta(days=5)  # use your own stored date
## article_delta = fetch_reader_document_list_api(docs_after_date.isoformat(), token=rkey)

article_delta = fetch_reader_document_list_api(location='archive', token=rkey)

client = genai.Client(api_key=gkey)
# article = article_delta[0]
articles = [x['html_content'] for x in article_delta][:30]

print("Article count is {}".format(len(articles)))
#exit()
## print(article); exit()

system_instruction = """
Role: You are an assistant summarizing articles that are of interest.
Focus on newly introduced techniques, tools, or approaches especially as
they relate to information security
Make the title a link to the source material starting the title with the top level domain linked and including the article name separated by a colon
Include an entry for every item
Include meta commentary on common sources and topics
Render output as stand alone valid HTML without any other intro
"""

response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=1000,
        temperature=0.1),
    contents=articles,
)

# cleanup html
text = response.text.rstrip("```").lstrip("```").lstrip('html')

filepath = 'page.html'
try:
  with open(filepath, 'w', encoding='utf-8') as f:
      f.write(text)
      print(f"Successfully wrote to {filepath}")
except Exception as e:
    print(f"Error writing to {filepath}: {e}")

# print(response)
