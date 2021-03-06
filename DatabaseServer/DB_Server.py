import sys
import json
import socket
import threading
from CommandHandler import command_handler
from Database import create_tables


class ClientThread (threading.Thread):
    def __init__(self, socket, addr, command):
        threading.Thread.__init__(self)
        self.socket = socket
        self.addr = addr
        self.command = command

    def run(self):
        if self.command:
            thread_lock.acquire()
            result = command_handler(self.command)
            thread_lock.release()

            if not result:
                result = {'status': 1, 'message': '[Server Error] Response is none.'}
            try:
                self.socket.send(json.dumps(result).encode('utf-8'))

            except socket.error as err:
                print('[Socket ERROR] Send data to client socket fail:', err)
            except socket.timeout as err:
                print('[Socket ERROR] Send data to client socket timeout:', err)
            except Exception as err:
                print('[Socket ERROR] Undefiend error:', err)

            finally:
                print('response:', result)
                self.socket.close()


if __name__ == '__main__':
    ip, port = '127.0.0.1', 10009

    if len(sys.argv) == 3:
        ip, port = sys.argv[1], int(sys.argv[2])
    else:
        print('Usage: python3 {} IP PORT'.format(sys.argv[0]))

    # Create database if not exist
    create_tables()

    # Create a thread lock to avoid race condition to the database
    thread_lock = threading.Lock()

    # Set up a socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    print('Starting up on {} port {}'.format(*server_address))
    server_sock.bind(server_address)
    server_sock.listen(30)

    while True:
        client_sock, client_address = server_sock.accept()
        print('Client connect:', client_address)

        command = None

        try:
            command = json.loads(client_sock.recv(2048).decode('utf-8'))
            print('Command receive:', command, '\n')

        except socket.error as err:
            print('[Socket ERROR] Receive data from client socket fail:', err)
        except socket.timeout as err:
            print('[Socket ERROR] Receive data from client socket timeout:', err)
        except Exception as err:
            print('[Socket ERROR] Undefiend error:', err)

        # Create threads to handle commands for each client
        try:
            client_thread = ClientThread(client_sock, client_address, command)
            client_thread.start()

        except Exception as err:
            print('[ERROR] Create thread fail:', err)
            continue
