import asyncio
import json
from uuid import UUID

import websockets

from node_launcher.logging import log
from websocket.models.channel_opening_invoices import ChannelOpeningInvoices
from websocket.models.users import Users
from websocket.utilities import get_server_id


class MainServer(object):
    def __init__(self):
        self.channel_opening_invoices = ChannelOpeningInvoices()
        self.users = Users()
        self.channel_opening_server = None

    async def run(self, websocket, path):
        data_string_from_client = await websocket.recv()

        # noinspection PyBroadException
        try:
            data_from_client = json.loads(data_string_from_client)
        except:
            log.error(
                'Error loading json',
                exc_info=True,
                data_string_from_client=data_string_from_client
            )
            return

        user_id = data_from_client.get('user_id', None)
        server_id = data_from_client.get('server_id', None)
        if not user_id and not server_id:
            log.error(
                'user_id and server_id missing',
                data_string_from_client=data_string_from_client
            )
            return
        if server_id not in [
            get_server_id('main'),
            get_server_id('invoices'),
            get_server_id('channels'),
            get_server_id('webapp')
        ]:
            log.error(
                'Invalid server_id',
                data_string_from_client=data_string_from_client
            )
            return
        try:
            UUID(user_id, version=4)
        except ValueError:
            log.error(
                'Invalid user_id',
                data_string_from_client=data_string_from_client
            )
            return

        # User registration
        if user_id and not server_id:
            await self.users.register(
                user_id=user_id,
                websocket=websocket
            )
            return

        # Server action dispatching
        data_from_server = data_from_client
        if server_id == get_server_id('webapp'):
            if data_from_server['type'] == 'inbound_capacity_request':
                self.channel_opening_invoices.add_invoice_package(
                    r_hash=data_from_server['invoice']['r_hash'],
                    package=data_from_server
                )
                log.debug(
                    'Received from server',
                    data_type='inbound_capacity_request'
                )
                return
        elif server_id == get_server_id('invoices'):
            if data_from_server['type'] == 'invoice_paid':
                invoice_data = data_from_server['invoice_data']
                package = self.channel_opening_invoices.get_invoice_package(
                    r_hash=invoice_data['r_hash']
                )
                if package is None:
                    log.debug(
                        'r_hash not found in channel_opening_invoices',
                        invoice_data=invoice_data
                    )
                    return

                log.debug('emit invoice_data', invoice_data=invoice_data)
                await self.users.send(
                    package['user_id'],
                    invoice_data
                )

                if package.get('reciprocation_capacity', None):
                    local_funding_amount = package['reciprocation_capacity']
                else:
                    local_funding_amount = int(package['form_data']['capacity'])

                sat_per_byte = int(package['form_data']['transaction_fee_rate'])
                data = dict(
                    server_id=get_server_id('main'),
                    user_id=package['user_id'],
                    type='open_channel',
                    remote_pubkey=package['parsed_pubkey'],
                    local_funding_amount=local_funding_amount,
                    sat_per_byte=sat_per_byte
                )
                await self.channel_opening_server.send(json.dumps(data))

        elif server_id == get_server_id('channels'):
            self.channel_opening_server = websocket


if __name__ == '__main__':
    main_server = MainServer()
    start_server = websockets.serve(main_server.run, 'localhost', 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
