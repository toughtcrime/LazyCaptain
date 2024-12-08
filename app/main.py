import logging
from database.client import RedisClient
from services.ssh import SSHManager
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    # redis_client = RedisClient(host = 'localhost', port = 6379)
    # redis_client.connect()
    ssh_client = SSHManager(username="ubuntu",password="123", 
                            server_ip="192.168.0.103", 
                            private_key_path="~/.ssh/id_ed25519", 
                            public_key_path="~/.ssh/id_ed25519.pub")
    ssh_client.connect()
    ssh_client.upload_public_key()
    ssh_client.connect_with_key()
    ssh_client.close_connection()

if __name__ == '__main__':
    main()