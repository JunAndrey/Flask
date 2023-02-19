import requests

# response = requests.post('http://127.0.0.1:5001/users',
#                          json={'username': 'banan',
#                                'password': 'sMFIKfvsjsnds', 'users_email': 'banan@gmail.com'})

response = requests.delete('http://127.0.0.1:5001/posts/68/7')

#
# response = requests.patch('http://127.0.0.1:5001/posts/66/5',
#                           json={'title': 'patched_it', 'description': 'bu_users_4'})

print(response.status_code)
print(response.json())

response = requests.get('http://127.0.0.1:5001/posts/all')
print(response.status_code)
print(response.json())
