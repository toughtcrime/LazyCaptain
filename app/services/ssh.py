import paramiko
import getpass
import logging
import os

logger = logging.getLogger(__name__)

class SSHManager:

    def __init__(self, username, password, server_ip):
        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.ssh_client = None

    def upload_public_key(self, public_key_path="~/.ssh/id_ed25519.pub"):
        """
        Upload the local SSH public key to the remote server's authorized_keys.

        Args:
            public_key_path (str): Path to the local public key file.
        """
        if not self.ssh_client:
            logger.error("No active SSH connection. Please connect first.")
            return

        try:
            # Expand the public key path
            public_key_path = os.path.expanduser(public_key_path)
            if not os.path.exists(public_key_path):
                logger.error(f"Public key file not found: {public_key_path}")
                return

            # Read the public key content
            with open(public_key_path, "r") as pubkey_file:
                public_key = pubkey_file.read()

            # Create the .ssh directory if it doesn't exist
            stdin, stdout, stderr = self.ssh_client.exec_command("mkdir -p ~/.ssh && chmod 700 ~/.ssh")
            stderr_output = stderr.read().decode()
            if stderr_output:
                logger.error(f"Error creating .ssh directory: {stderr_output}")
                return

            # Append the public key to authorized_keys
            stdin, stdout, stderr = self.ssh_client.exec_command("echo '{}' >> ~/.ssh/authorized_keys".format(public_key.strip()))
            stderr_output = stderr.read().decode()
            if stderr_output:
                logger.error(f"Error appending public key to authorized_keys: {stderr_output}")
                return

            # Set proper permissions for authorized_keys
            stdin, stdout, stderr = self.ssh_client.exec_command("chmod 600 ~/.ssh/authorized_keys")
            stderr_output = stderr.read().decode()
            if stderr_output:
                logger.error(f"Error setting permissions on authorized_keys: {stderr_output}")
                return

            logger.info(f"Successfully uploaded public key to {self.server_ip}")
        except Exception as e:
            logger.error(f"Failed to upload public key to {self.server_ip}: {e}")

    
    def connect(self):
        """Establish an SSH connection using the provided credentials."""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.server_ip,
                username=self.username,
                password=self.password
            )
            print(f"Successfully connected to {self.server_ip}")
        except Exception as e:
            print(f"Failed to connect to {self.server_ip}: {e}")
            self.ssh_client = None
    
    def close_connection(self):
        """Close the SSH connection."""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info(f"Connection to {self.server_ip} closed.")
    