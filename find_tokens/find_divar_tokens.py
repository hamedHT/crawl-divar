import requests

url = 'https://api.divar.ir/v8/postlist/w/search'

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://divar.ir/",
    "Origin": "https://divar.ir",
}

json_payload = {
    "search_data": {
        "form_data": {
            "data": {
                "category": {
                    "str": {
                        "value": "residential-sell"
                    }
                }
            }
        },
        "server_payload": {
            "@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
            "additional_form_data": {
                "data": {
                    "sort": {
                        "str": {
                            "value": "sort_date"
                        }
                    }
                }
            }
        }
    },
    "city_ids": ["1"]
}

list_of_tokens = []

while len(list_of_tokens) < 100:
    res = requests.post(url, json=json_payload, headers=headers)

    if res.status_code != 200:
        print(f"error: {res.status_code} - {res.text}")
        break

    data = res.json()

    new_tokens = 0
    if 'list_widgets' in data:
        for widget in data['list_widgets']:
            if widget.get('widget_type') == 'POST_ROW':
                token = widget.get('data', {}).get('token')
                if token and token not in list_of_tokens:
                    list_of_tokens.append(token)
                    new_tokens += 1
                    print(f"[{len(list_of_tokens)}] {token}")

    print(f"---  this page: {new_tokens} token | sum: {len(list_of_tokens)} ---")

    if new_tokens == 0:
        print("Not found token")
        break

    pagination = data.get('pagination', {})
    if not pagination.get('has_next_page', False):
        print("the next page has not exist")
        break

    pagination_data = pagination.get('data', {})
    if not pagination_data:
        print("the information of next page not found")
        break

    json_payload["pagination_data"] = pagination_data

with open('tokens.txt', 'w', encoding='utf8') as f:
    f.write(','.join(list_of_tokens))

print(f"\n sum of tokens: {len(list_of_tokens)}")
print(list_of_tokens)
