from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker, LeakyBucket
from crawler.report import Reporter
from queue import Queue
from threading import Event

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")

        self.throttle_q = Queue(maxsize=1)
        self.frontier = frontier_factory(config, restart, self.throttle_q)
        self.workers = list()
        self.worker_factory = worker_factory
        self.word_reporter = Reporter(config, restart)

        self.term_event = Event()
        self.leaky_bucket = LeakyBucket(config, self.throttle_q, self.term_event)

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.word_reporter)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.leaky_bucket.start()
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
            
        self.term_event.set()
        self.leaky_bucket.join()
