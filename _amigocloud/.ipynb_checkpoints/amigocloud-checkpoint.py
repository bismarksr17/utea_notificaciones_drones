#!/usr/bin/env python
# coding: utf-8

# In[15]:


import json
import requests


# In[16]:


BASE_URL = 'https://app.amigocloud.com'
API_URL = BASE_URL + '/api/v1'


# In[17]:


class AmigoCloudError(Exception):
    
    def __init__(self, message, response=None):
        self.message = message
        self.response = response
        self.text = getattr(self.response, 'text', None)

    def __str__(self):
        if self.text:
            return self.message + '\n' + self.text
        return self.message


# In[23]:


class AmigoCloud(object):

    def __init__(self, token, base_url=BASE_URL):
        self.base_url = base_url
        self.api_url = base_url + '/api/v1'
        self.token = token

    def build_url(self, url):
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return self.api_url + url
        return '/'.join(s.strip('/') for s in (self.api_url, url))

    def get(self, url, params=None):
        full_url = self.build_url(url)
        params = params or {}
        if self.token:
            params.setdefault('token', self.token)

        response = requests.get(full_url, params=params)
        if response.status_code != 200:
            raise AmigoCloudError('Failed to retrieve data: ' + response.text)

        return json.loads(response.text)

    def execute_sql(self, project_id, query, limit=100):
        url = f'/projects/{project_id}/sql'
        offset = 0
        while True:
            params = {'query': query, 'limit': limit, 'offset': offset}
            response = self.get(url, params)
            yield response  # This will return the current page of results
            
            # Assuming 'data' is the key where the results are stored
            data = response.get('data', [])
            if len(data) < limit:
                break  # No more pages, exit loop
            
            offset += limit  # Update the offset to get the next page


# In[24]:


# Uso:
token = 'A:cf5xrxU3HgHj9FkLMiY5wW9LBFmvYDQG2TQ5FY'
project_id = '31874'
query = 'SELECT * FROM dataset_322082'

amigo_client = AmigoCloud(token)
x = 0
for page in amigo_client.execute_sql(project_id, query):
    x = x + len(page['data'])
    print(x)


# In[13]:


data['data']


# In[ ]:





# In[ ]:





# In[ ]:




