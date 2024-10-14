import os
import requests
import random
import itertools
import hashlib
import pickle
import time
import concurrent.futures
import logging
from fake_useragent import UserAgent
from requests import Session

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

class RotatingProxySession(Session):
    def __init__(self, main_proxy=None, cache_dir="proxy_cache", response_cache_dir="response_cache", refresh_interval=360):
        super().__init__()
        self.main_proxy = main_proxy
        self.cache_dir = cache_dir
        self.response_cache_dir = response_cache_dir
        self.refresh_interval = refresh_interval
        self.refresh_checkpoint = os.path.join(self.cache_dir, "last_refresh_checkpoint.pkl")

        self.socks5_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"
        self.socks4_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"
        self.http_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"

        self.socks5_cache = os.path.join(self.cache_dir, "socks5.txt")
        self.socks4_cache = os.path.join(self.cache_dir, "socks4.txt")
        self.http_cache = os.path.join(self.cache_dir, "http.txt")
        self._create_cache_dir(self.cache_dir)
        self._create_cache_dir(self.response_cache_dir)

        # Load proxies (from cache or fetch if cache is missing)
        self.socks5_proxies = self._load_proxies(self.socks5_url, self.socks5_cache)
        self.socks4_proxies = self._load_proxies(self.socks4_url, self.socks4_cache)
        self.http_proxies = self._load_proxies(self.http_url, self.http_cache)

        # Combine all proxies into one list
        self._initialize_all_proxies()

        # List to store successful proxies
        self.successful_proxies = []

        # Initialize fake user agent
        self.user_agent = UserAgent()

    def _create_cache_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def _fetch_and_cache_proxies(self, url, cache_file):
        response = requests.get(url)
        proxies = response.text.strip().split('\n')
        with open(cache_file, 'w') as f:
            f.write("\n".join(proxies))
        return proxies

    def _load_proxies(self, url, cache_file):
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                proxies = f.read().strip().split('\n')
        else:
            proxies = self._fetch_and_cache_proxies(url, cache_file)
        return proxies

    def _initialize_all_proxies(self):
        self.all_proxies = list(itertools.chain(
            [('socks5', proxy) for proxy in self.socks5_proxies],
            [('socks4', proxy) for proxy in self.socks4_proxies],
            [('http', proxy) for proxy in self.http_proxies]
        ))

    def _get_last_refresh_time(self):
        if os.path.exists(self.refresh_checkpoint):
            with open(self.refresh_checkpoint, 'rb') as f:
                return pickle.load(f)
        return 0  # If no checkpoint exists, assume the proxies need to be refreshed

    def _set_last_refresh_time(self, refresh_time):
        with open(self.refresh_checkpoint, 'wb') as f:
            pickle.dump(refresh_time, f)

    def _refresh_proxies_if_needed(self):
        last_refresh_time = self._get_last_refresh_time()
        current_time = time.time()
        if current_time - last_refresh_time > self.refresh_interval:
            self.socks5_proxies = self._fetch_and_cache_proxies(self.socks5_url, self.socks5_cache)
            self.socks4_proxies = self._fetch_and_cache_proxies(self.socks4_url, self.socks4_cache)
            self.http_proxies = self._fetch_and_cache_proxies(self.http_url, self.http_cache)
            self._initialize_all_proxies()
            self._set_last_refresh_time(current_time)

    def _get_random_proxy(self):
        self._refresh_proxies_if_needed()
        if self.successful_proxies:
            return random.choice(self.successful_proxies)
        protocol, proxy = random.choice(self.all_proxies)
        return {protocol: f"{protocol}://{proxy}"}

    def _generate_cache_key(self, method, url, params=None, data=None):
        key = f"{method}:{url}"
        if params:
            key += f":{sorted(params.items())}"
        if data:
            key += f":{data}"
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def _get_cache_path(self, cache_key):
        return os.path.join(self.response_cache_dir, f"{cache_key}.pkl")

    def _load_cached_response(self, cache_key):
        cache_path = self._get_cache_path(cache_key)
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as cache_file:
                return pickle.load(cache_file)
        return None

    def _save_response_to_cache(self, cache_key, response):
        cache_path = self._get_cache_path(cache_key)
        with open(cache_path, 'wb') as cache_file:
            pickle.dump({
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.content
            }, cache_file)

    def request(self, method, url, retries=5, backoff_factor=1, disable_cache=True, **kwargs):
        # Check if caching should be disabled
        if not disable_cache:
            cache_key = self._generate_cache_key(method, url, kwargs.get('params'), kwargs.get('data'))
            cached_response = self._load_cached_response(cache_key)
            if cached_response:
                response = requests.Response()
                response.status_code = cached_response['status_code']
                response.headers.update(cached_response['headers'])
                response._content = cached_response['content']
                return response

        proxies = [self.main_proxy] if self.main_proxy else []
        proxies.extend([self._get_random_proxy() for _ in range(retries)])

        for attempt, proxy in enumerate(proxies, 1):
            kwargs['proxies'] = proxy

            # Set a random user agent
            kwargs['headers'] = kwargs.get('headers', {})
            kwargs['headers']['User-Agent'] = self.user_agent.random

            try:
                response = super().request(method, url, **kwargs)

                # Store the successful proxy if it's not the main proxy
                if proxy != self.main_proxy:
                    self.successful_proxies.append(proxy)

                # Only save to cache if not disabled
                if not disable_cache:
                    self._save_response_to_cache(cache_key, response)

                return response
            except requests.exceptions.RequestException:
                if attempt < len(proxies):
                    time.sleep(backoff_factor * attempt)
        raise requests.exceptions.RequestException("Failed to fetch the content after several retries.")

    def fetch_urls_concurrently(self, urls, max_workers=5, retries=5, backoff_factor=1, disable_cache=False):
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.request, 'GET', url, retries, backoff_factor, disable_cache): url
                for url in urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    response = future.result()
                    if response and hasattr(response, 'content'):
                        results[url] = response
                    else:
                        results[url] = None
                except Exception as e:
                    results[url] = None
                    logging.error(f"Failed to fetch {url}. Error: {e}")
        return results

def get(url, **kwargs):
    session = RotatingProxySession()
    try:
        response = session.get(url=url, **kwargs)
        if response:
            print("Successfully fetched the content.")
            return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
