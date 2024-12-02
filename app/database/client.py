import redis
import os
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    
    def __init__(self, host='localhost', port=6379, db=0):
        """Initilize the Redis with connection parameters."""
        self.host = os.getenv('REDIS_HOST', host)
        self.port = int(os.getenv('REDIS_PORT', port))
        self.db = int(os.getenv('REDIS_DB',0))
        self.connection = redis.Redis(
                host = self.host,
                port = self.port,
                db = self.db,
                decode_responses = True
            )
        self.client = self.connection
        
    
    def connect(self):
        """Establish a connection to the Redis database"""
        logger.debug('Attempting to connect to Redis...')
        try:
            self.connection.ping()
            logger.info(f'Connected to Redis at {self.host}:{self.port}')
        except redis.ConnectionError as e:
            logger.error(f'Error handling to Redis: {e}')
            self.connection = None
            raise


    def get_connection(self):
        """Return the Redis connection. Connect if not already connected."""
        if not self.connection:
            self.connect()
        return self.connection