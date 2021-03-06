from google.protobuf.json_format import MessageToDict
from grpc._channel import _Rendezvous

from lnd_grpc.lnd_grpc import Client
from website.logger import log


class Channel(object):
    def __init__(self,
                 rpc: Client,
                 capacity: int,
                 commit_fee: int = 0,
                 local_balance: int = 0, remote_balance: int = 0,
                 remote_pubkey: str = None, chan_id: int = None,
                 channel_point: str = None,
                 active: bool = None,
                 **kwargs):
        self.rpc = rpc
        self.data = kwargs
        self.info = None
        if chan_id is not None:
            self.chan_id = int(chan_id)
        else:
            self.chan_id = None

        if self.chan_id is not None and not self.data.get('close_height', False):
            try:
                self.info = MessageToDict(self.rpc.get_chan_info(self.chan_id))
            except _Rendezvous as e:
                log.error(
                    'get_chan_info',
                    exc_info=True
                )

        self.remote_pubkey = remote_pubkey
        if remote_pubkey is None and self.info is not None:
            raise Exception()
        if not remote_pubkey:
            self.remote_pubkey = kwargs['remote_node_pub']
        self.channel_point = channel_point
        self.capacity = int(capacity)
        self.local_balance = int(local_balance)
        self.remote_balance = int(remote_balance)
        self.commit_fee = int(commit_fee)
        self.is_active = bool(active)

    @property
    def available_capacity(self) -> int:
        return self.capacity - self.commit_fee

    @property
    def balance(self) -> int:
        return int((self.local_balance / self.available_capacity) * 100)

    @property
    def is_mine(self) -> bool:
        return self.balance > 80

    @property
    def is_yours(self) -> bool:
        return self.balance < 20

    @property
    def is_pending(self) -> bool:
        return self.chan_id is None
