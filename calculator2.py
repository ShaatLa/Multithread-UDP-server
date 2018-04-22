import json
import time
import lib

log = lib.log()

with open('calculator2.cfg', 'r') as dispatcher_cfg:
    cfg = json.load(dispatcher_cfg)
    addr = str(cfg['addr'])
    port = cfg['port']
    sleep_time = cfg['time']
    disable_time = cfg['disable_time']

    dispatcher_addr = str(cfg['dispatcher_addr'])
    dispatcher_port = cfg['dispatcher_port']

class CalcSocket(lib.SocketClass):
    def __init__(self, addr, port):
        super(CalcSocket, self).__init__(addr, port)
        self._sock.bind((addr, port))
        self._sock.settimeout(3)

    def recvfrom(self, buffersize=1024):
        data, addr = self._sock.recvfrom(buffersize)
        return data, addr

    def send_data(self, data, addr):
        self._sock.sendto(data.encode('utf-8'), addr)

    def close(self, conn):
        self._sock.close()
        print 'Connection closed.'

    def calculation(self, data1, data2):
        self.data1 = data1
        self.data2 = data2
        return self.data1 + self.data2

calculator = CalcSocket(addr, port)

log.info('Calculator is online on %s:%d\n' % (addr, port))

while True:
    if lib.break_calculator() == 10:
        log.info('Calculator is broken...')
        time.sleep(60)

    try:
        data, addr = calculator.recvfrom()
        if data == 'ping':
            response = 'online'
            calculator.send_data(response, addr)

        else:
            client_data = []
            log.info('Data recived - %s' % data)

            for i in data.split(' '):
                client_data.append(i)
            task_num = '{} {}'.format(client_data[0], client_data[1])
            calculation = calculator.calculation(int(client_data[2]), int(client_data[3]))
            log.info('Calculating...')
            time.sleep(sleep_time)

            response = '{} {}'.format(task_num, calculation)
            log.info('Result - %s\n' % response)

            calculator.send_data(response, addr)

    except lib.socket.timeout:
        pass