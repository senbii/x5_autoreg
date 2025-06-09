import requests


def get_browser_ws(api_key, browser_id):
    url = "http://127.0.0.1:54345/browser/start"
    payload = {"id": browser_id, "debug_port": ""}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == 0:
            return data["data"]["ws"]["selenium"]
        else:
            error_msg = data.get("msg", "Unknown error")
            raise Exception(f"BitBrowser error: {error_msg}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")


def close_browser(api_key, browser_id):
    url = "http://127.0.0.1:54345/browser/stop"
    payload = {"id": browser_id}
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except:
        return {}
