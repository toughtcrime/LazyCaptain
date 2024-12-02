import logging
from database.client import RedisClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    redis_client = RedisClient(host = 'localhost', port = 6379)
    redis_client.connect()

if __name__ == '__main__':
    main()