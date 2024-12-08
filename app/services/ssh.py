import paramiko
import getpass
import logging
import os

logger = logging.getLogger(__name__)

class SSHManager:
    """Class to handle SSH public key copying and key-based connections to remote servers."""

    def __init__(self, username, password, server_ip, private_key_path, public_key_path):
        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.ssh_client = None
        self.private_key_path = os.path.expanduser(private_key_path)
        self.public_key_path = public_key_path

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
    
    def connect_with_key(self):
            """
            Connect to a server via SSH using a private key.

            Returns:
                bool: True if the connection is successful, False otherwise.
            """
            # Validate the private key type
            is_valid, key_type_or_error = self.validate_private_key()
            if not is_valid:
                print(f"Key validation failed: {key_type_or_error}")
                return False

            try:
                print(f"Connecting to {self.server_ip} using {key_type_or_error} key...")

                match key_type_or_error:
                    case "RSA":
                        key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
                    case "Ed25519":
                        key = paramiko.Ed25519Key.from_private_key_file(self.private_key_path)
                    case "DSA":
                        key = paramiko.DSSKey.from_private_key_file(self.private_key_path)
                    case "ECDSA":
                        key = paramiko.ECDSAKey.from_private_key_file(self.private_key_path)
                    case _:
                        print(f"Unhandled key type '{key_type_or_error}' during connection.")
                        return False

                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(
                    hostname=self.server_ip,
                    username=self.username,
                    pkey=key
                )
                print(f"Successfully connected to {self.server_ip} using the {key_type_or_error} key.")
                return True
            except paramiko.AuthenticationException:
                print(f"Authentication failed when connecting to {self.server_ip}.")
            except FileNotFoundError:
                print(f"Private key file not found: {self.private_key_path}.")
            except Exception as e:
                print(f"An error occurred while connecting to {self.server_ip}: {e}")
            return False

    
    def validate_private_key(self):
        """
        Validate the type of the private key file.

        Returns:
            tuple: (bool, str) where the first value indicates if the key is valid,
                   and the second value is the key type or error message.
        """
        try:
            # Try to load the key as an RSA key
            paramiko.RSAKey.from_private_key_file(self.private_key_path)
            return True, "RSA"
        except paramiko.ssh_exception.PasswordRequiredException:
            return False, "Password-protected RSA key is not supported in this script."
        except paramiko.ssh_exception.SSHException:
            pass  # If not RSA, continue to other key types.

        try:
            # Try to load the key as an Ed25519 key
            paramiko.Ed25519Key.from_private_key_file(self.private_key_path)
            return True, "Ed25519"
        except paramiko.ssh_exception.SSHException:
            pass  # If not Ed25519, continue to other key types.

        try:
            # Try to load the key as a DSA key
            paramiko.DSSKey.from_private_key_file(self.private_key_path)
            return True, "DSA"
        except paramiko.ssh_exception.SSHException:
            pass  # If not DSA, continue to other key types.

        try:
            # Try to load the key as an ECDSA key
            paramiko.ECDSAKey.from_private_key_file(self.private_key_path)
            return True, "ECDSA"
        except paramiko.ssh_exception.SSHException:
            pass  # If not ECDSA, no other types are supported.

        return False, "Unsupported or invalid private key format."