import urllib.request
import os

base_dir = r"D:\Helix_Zero1\CMS\static"
js_dir = os.path.join(base_dir, "js")
css_dir = os.path.join(base_dir, "css")

os.makedirs(js_dir, exist_ok=True)
os.makedirs(css_dir, exist_ok=True)

# Validated URLs
TARGETS = [
    (os.path.join(js_dir, "fornac.js"), "https://unpkg.com/fornac@latest/dist/scripts/fornac.js"),
    (os.path.join(css_dir, "fornac.css"), "http://rna.tbi.univie.ac.at/forna/css/fornac.css"), # Direct from source
    (os.path.join(js_dir, "jquery.min.js"), "https://code.jquery.com/jquery-3.6.0.min.js"),
    (os.path.join(js_dir, "d3.min.js"), "https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.17/d3.min.js")
]

for path, url in TARGETS:
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, path)
        size = os.path.getsize(path)
        print(f"  -> Saved to {path} ({size} bytes)")
    except Exception as e:
        print(f"  -> Failed: {e}")
