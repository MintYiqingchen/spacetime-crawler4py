import os
import shelve
import glob

from threading import Lock
from queue import Queue, Empty

from utils import get_logger, get_urlhash

class Reporter(object):
    def __init__(self, config, restart):
        self.logger = get_logger("REPORTER")
        self.config = config
        
        save_files = glob.glob(self.config.word_file + '.*')
        if not save_files and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.word_file}, "
                f"starting from seed.")
        elif save_files and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.word_file}, deleting it.")
            for sf in save_files:
                os.remove(sf)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.word_file)
        self.save_lock = Lock()

    def add_words(self, url, words):
        if words is None:
            return
        urlhash = get_urlhash(url)
        with self.save_lock:
            self.save[urlhash] = (url, tuple(words))
            self.save.sync()