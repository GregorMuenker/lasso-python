import atexit
import signal
import sys

import pysolr
from sshtunnel import SSHTunnelForwarder
import os
import dotenv

dotenv.load_dotenv()

server = SSHTunnelForwarder(
    os.environ["SERVER_ADDRESS"],
    ssh_username=os.environ["SERVER_USER"],
    ssh_password=os.environ["SERVER_PASSWORD"],
    remote_bind_address=('127.0.0.1', 8983),
    local_bind_address=('127.0.0.1', 8983),
)

server.start()

def handle_exit(*args):
    global server
    server.stop()
    sys.exit(0)


atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

while True:
    pass