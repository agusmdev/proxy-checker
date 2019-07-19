from operator import itemgetter
import requests
from threading import Thread
from collections import defaultdict, OrderedDict
import concurrent.futures
import json


class ProxyBenchmark:
    def __init__(self, slice_size=100, proxies_path='proxies.txt', threaded=True, attempts=3):
        self.proxies = list(set(open(proxies_path, 'r').read().split('\n')))
        self.attempts = attempts
        self.checker_url = 'https://www.google.com.ar/search?source=hp&q=hola&oq=hola'
        self.response_times = defaultdict(list)
        self.slice_size = min(slice_size, len(self.proxies))
        self.size = len(self.proxies)/self.slice_size
        self.slices = [(i*slice_size, (i+1)*slice_size) for i in range(int(self.size))]

    def check_proxy(self, proxy):
        proxy_dict = {'https': f'https://{proxy}'}
        try:
            r = requests.get(self.checker_url, proxies=proxy_dict, timeout=5)
            r = r.elapsed.total_seconds()
        except requests.exceptions.RequestException:
            r = 999
        self.response_times[proxy].append(r)
        
    def start_checking(self):
        for i in range(self.attempts):
            for idx, (start, end) in enumerate(self.slices):
                print("checking proxies---- attempt: {}, slice: {}".format(i, idx))
                t = [Thread(target=self.check_proxy, args=(proxy,)) for proxy in self.proxies[start:end]]
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

    def save(self):
        self.make_dict()
        self.sort_times()
        dump = [ip for ip, time in self.meaned_dict.items() if time < 50]
        json.dump(self.meaned_dict, open("proxies.json", "w")) # , indent=4)


if __name__ == '__main__':
    x = ProxyBenchmark(attempts=1, slice_size=1000, proxies_path="proxy_list.txt")
    x.start_checking()
    x.save()
