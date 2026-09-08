import os
import logging
from leakybucket import (
    LeakyBucket,
    AsyncLeakyBucket
)
from leakybucket.persistence import (
    InMemoryLeakyBucketStorage,
    RedisLeakyBucketStorage
)
from dotenv import load_dotenv

_logger = logging.getLogger(__name__)

load_dotenv()

MAX_RATE = 30 # max requests
TIME_PERIOD = 1 # per second

storage = InMemoryLeakyBucketStorage(
    max_rate=MAX_RATE, 
    time_period=TIME_PERIOD
)
throttler = LeakyBucket(storage)
async_throttler = AsyncLeakyBucket(storage)