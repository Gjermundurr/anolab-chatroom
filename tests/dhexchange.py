import socket
from M2Crypto import DH as M2DH
from dhke import DH, DH_SIZE, LEN_PK


class server:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dh_params = M2DH.gen_params(DH_SIZE, 2)



