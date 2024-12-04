import logging
from database.client import RedisClient
from services.ssh import SSHManager
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    #redis_client = RedisClient(host = 'localhost', port = 6379)
    # redis_client.connect()
    ssh_client = SSHManager("ubuntu","123", "192.168.0.103")
    ssh_client.connect()
    ssh_client.upload_public_key()
    ssh_client.close_connection()

if __name__ == '__main__':
    main()