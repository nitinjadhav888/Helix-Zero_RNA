import urllib.request
import urllib.error

base = "https://unpkg.com/fornac@latest/"
candidates = [
    "dist/css/fornac.css",
    "css/fornac.css",
    "styles/fornac.css",
    "fornac.css",
    "dist/fornac.css"
]

for path in candidates:
    url = base + path
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"CSS FOUND: {url}")
                break
    except Exception as e:
        print(f"404: {url}")
