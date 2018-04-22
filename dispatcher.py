import json
import threading
import Queue
import lib

log = lib.log()

calculators = []

with open('dispatcher.cfg', 'r') as dispatcher_cfg:
    cfg = json.load(dispatcher_cfg)
    addr = str(cfg['addr'])
    port = cfg['port']
    calculators_kw = cfg['calculators']

    for i in calculators_kw:
        v = calculators_kw.get(i)
        l = []
        l.append(str(v[0]))
        l.append(int(v[1]))
        calculators.append(tuple(l))


class DispatcherSocket(lib.SocketClass):
    def __init__(self, addr, port):
        super(DispatcherSocket, self).__init__(addr, port)
        self._sock.bind((addr, port))

    def recvfrom(self, buffersize=1024):
        data, addr = self._sock.recvfrom(buffersize)
        return data, addr

    def settimeout(self, num):
        self._sock.settimeout(num)

    def send_data(self, calc_addr, data):
        self._sock.sendto(data.encode('utf-8'), calc_addr)

    def close(self, conn):
        self._sock.close()
        print 'Connection closed.'


class CalcConnection(lib.SocketClass):
    def __init__(self, addr, port):
        super(CalcConnection, self).__init__(addr, port)
        self._sock.connect((addr, port))
        self._sock.settimeout(3)


def calc_thread(calculators, dispatcher_sock, queue):
    # The main process in the thread.
    # Starting connection with calculators and trying to find one online:
    for i in range(len(calculators)):
        sock = CalcConnection(*calculators[i])
        # Trying to find calculator online
        sock.send_data('ping')
        try:
            ping = sock.recv_data()

            if ping == 'online':
                log.info('Calculator %s online.' % (i + 1))
                # If dispathcer found one online, it takes task from queue, sands it to calculator and waits
                # for the result.
                try:
                    task, client = queue.get()

                    sock.send_data(task)
                    sock.settimeout(None)
                    result = sock.recv_data()

                    if result:
                        dispatcher_sock.send_data(client, result)
                        queue.task_done()
                        break
                    else:
                        break
                except Exception as ex:
                    log.debug('Task exception: %s' % ex)

            else:
                log.debug('Wrong response')

        except Exception as ex:
            log.debug('Calculator exception: %s' % ex)


# Main socket
dispatcher = DispatcherSocket(addr, port)

log.info('Online. Waiting for data...')

# Tasks queue.
calc_queue = Queue.Queue()

clients = []

# Main loop
while True:
    # Trying to receive tasks from clients
    try:
        data, addr = dispatcher.recvfrom()

        if addr not in calculators:
            log.info('Data received - %s from client %s.' % (data, addr))

            # Putting task to the queue.All tasks keep here, queue is thread safe,
            # so the task deletes from queue only when it done.
            calc_queue.put((data, addr))

            # Starting thread for the current task
            calculator_thread = threading.Thread(target=calc_thread, args=(calculators,
                                                                           dispatcher,
                                                                           calc_queue))
            calculator_thread.start()

        else:
            log.info(data)

    except Exception as ex:
        log.debug("Exception: %s. Checking the queue..." % ex)

        # If no new data from clients, keep sending tasks from the queue.
        if not calc_queue.empty():
            print "queue tasks"
            calculator_thread = threading.Thread(target=calc_thread, args=(calculators,
                                                                           dispatcher,
                                                                           calc_queue))
            calculator_thread.start()

