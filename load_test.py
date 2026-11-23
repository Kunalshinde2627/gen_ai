
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.exceptions import RequestException

URL = "https://taxsaathi-api.onrender.com/health"


def test_api(i):
    start = time.time()

    try:
        response = requests.get(URL, timeout=60)
        duration = time.time() - start

        return (
            f"Request {i}: Status {response.status_code}, "
            f"Time {duration:.2f}s"
        )

    except RequestException as e:
        return f"Request {i}: Error - {e}"


with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(test_api, range(1, 4))

for result in results:
    print(result)
