import urllib.request
import os

base_dir = r"D:\Helix_Zero1\CMS\static"
js_dir = os.path.join(base_dir, "js")
css_dir = os.path.join(base_dir, "css")

os.makedirs(js_dir, exist_ok=True)
os.makedirs(css_dir, exist_ok=True)

urls = {
    os.path.join(js_dir, "fornac.js"): "https://cdn.jsdelivr.net/npm/fornac@0.2.1/dist/scripts/fornac.js",
    os.path.join(css_dir, "fornac.css"): "https://cdn.jsdelivr.net/npm/fornac@0.2.1/dist/css/fornac.css",
    os.path.join(js_dir, "jquery.min.js"): "https://code.jquery.com/jquery-3.6.0.min.js",
    os.path.join(js_dir, "d3.min.js"): "https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js"
}

for path, url in urls.items():
    print(f"Downloading {url} to {path}...")
    try:
        urllib.request.urlretrieve(url, path)
        print("Success.")
    except Exception as e:
        print(f"Failed: {e}")
