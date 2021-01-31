import os
import shelve
import glob
from utils import get_logger, get_urlhash, normalize, UrlInfo
from scraper import is_valid
from queue import Queue, Empty
from threading import Lock

class Frontier(object):
    def __init__(self, config, restart, throttle_q):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = Queue()
        
        save_files = glob.glob(self.config.save_file + '.*')
        if not save_files and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif save_files and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            for sf in save_files:
                os.remove(sf)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        self.save_lock = Lock()

        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

        self.throttle_q = throttle_q

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for urlInfo in self.save.values():
            if not urlInfo.completed and is_valid(urlInfo.url):
                self.to_be_downloaded.put(urlInfo.url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        self.throttle_q.get() # get token to do throttle

        try: # exit when the queue keep empty for a long time
            return self.to_be_downloaded.get(True, self.config.time_delay*10.0)
        except Empty:
            return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        
        should_put = False
        with self.save_lock:
            if urlhash not in self.save:
                self.save[urlhash] = UrlInfo(url)
                self.save.sync()
                should_put = True
        
        if should_put:
            self.to_be_downloaded.put(url)
    
    def mark_url_complete(self, url, urlInfo):
        urlhash = get_urlhash(url)
        with self.save_lock:
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = urlInfo
            self.save.sync()
