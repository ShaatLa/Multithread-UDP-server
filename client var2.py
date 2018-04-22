# This type of client always wait result of every task and send new task only when the previous is done.

import json
import random
import time
import lib

log = lib.log()

with open('client.cfg', 'r') as dispatcher_cfg:
    """Parsing config file"""
    cfg = json.load(dispatcher_cfg)
    addr = str(cfg['addr'])
    port = cfg['port']
    sleep_time = cfg['timer']


class ClientSocket(lib.SocketClass):
    def __init__(self, addr, port):
        super(ClientSocket, self).__init__(addr, port)
        self._sock.connect((addr, port))
        self._sock.settimeout(10)


client = ClientSocket(addr, port)

log.info('Client is online on %s:%d' % (addr, port))

stat_send = 0
stat_recv = 0
task_num = 1

while True:

    # Main client's loop.

    timer = time.time()
    data = 'Task {}: {} {}'.format(task_num, random.randint(1, 100), random.randint(100, 1000))
    task_num += 1

    log.info('Sending: %s' % data)
    client.send_data(data)
    timer = time.time()
    task_sent = True
    stat_send += 1

    task_not_done = True

    while task_not_done:
        try:
            data = client.recv_data()
            log.info('Result: %s' % data)
            task_not_done = False
            stat_recv += 1
        except lib.socket.error as ex:
            log.debug('%s. Waiting for result...' % ex)

    timer = time.time() - timer
    log.info('Packets send: %d, Packets recived: %d, Packets lost: %d, Waiting time: %d sec' % (
                                                                                        stat_send,
                                                                                        stat_recv,
                                                                                        (stat_send - stat_recv),
                                                                                        round(timer, 2)))
    time.sleep(sleep_time)
