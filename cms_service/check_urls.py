import urllib.request
import urllib.error

candidates = [
    "https://unpkg.com/fornac@0.2.1/dist/scripts/fornac.js",
    "https://unpkg.com/fornac@latest/dist/scripts/fornac.js",
    "https://cdn.jsdelivr.net/npm/fornac@0.2.1/dist/scripts/fornac.js",
    "https://raw.githubusercontent.com/ViennaRNA/forna/master/dist/js/fornac.js",
    "https://cdnjs.cloudflare.com/ajax/libs/fornac/0.2.1/scripts/fornac.js"
]

for url in candidates:
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(f"FOUND: {url}")
                # Try CSS partner
                css_url = url.replace("scripts/fornac.js", "css/fornac.css").replace("js/fornac.js", "css/fornac.css")
                try:
                    req_css = urllib.request.Request(css_url, method='HEAD')
                    with urllib.request.urlopen(req_css) as r_css:
                        if r_css.status == 200:
                            print(f"  CSS FOUND: {css_url}")
                except:
                    print(f"  CSS MISSING for {css_url}")
                break
    except urllib.error.HTTPError as e:
        print(f"404: {url}")
    except Exception as e:
        print(f"Error {url}: {e}")
