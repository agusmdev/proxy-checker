from operator import itemgetter
import requests
from threading import Thread
from collections import defaultdict, OrderedDict
import concurrent.futures


class ProxyBenchmark:
    def __init__(self, slice_size=100, proxies_path='proxies.txt', threaded=True, attempts=3):
        self.proxies = open(proxies_path, 'r').read().split('\n')
        self.attempts = attempts
        self.checker_url = 'https://www.google.com.ar/search?source=hp&q=hola&oq=hola'
        self.response_times = defaultdict(list)
        self.slice = slice_size

    def check_proxy(self, proxy):
        proxy_dict = {'https': f'https://{proxy}'}
        try:
            r = requests.get(self.checker_url, proxies=proxy_dict, timeout=5)
            r = r.elapsed.total_seconds()
        except requests.exceptions.RequestException:
            r = 999
        self.response_times[proxy].append(r)
        
    def start_checking(self):
        t = [Thread(target=self.check_proxy, args=(proxy,)) for proxy in self.proxies]
        [i.start() for i in t]
        [i.join() for i in t]
    
    def pooled(self):
        for _ in range(self.attempts):
            with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
                executor.map(self.check_proxy, self.proxies)
    
    def sort_times(self):
        self.response_times = OrderedDict(sorted(self.response_times.items(), key=itemgetter(1)))
        self.meaned_dict = OrderedDict(sorted(self.meaned_dict.items(), key=itemgetter(1)))
        
    
    def mean(self, times):
        return sum(times)/self.attempts
        
        
    def make_dict(self):
        self.meaned_dict = {proxy: self.mean(times) for proxy, times in self.response_times.items()}

