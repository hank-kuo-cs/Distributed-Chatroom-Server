import sys
import socket
import json
import threading
from CommandHandler import command_handler
from AppServerManagement import AppServerManageMent
from ServerMonitor import ServerMonitor


class ClientThread (threading.Thread):
    def __init__(self, clinet_socket, addr, client_command, app_server_management):
        threading.Thread.__init__(self)
        self.socket = clinet_socket
        self.addr = addr
        self.command = client_command
        self.app_server_management = app_server_management
        self.daemon = True

    def run(self):
        if self.command:
            thread_lock.acquire()
            result = command_handler(self.command, self.app_server_management)
            thread_lock.release()

            if not result:
                result = {'status': 1, 'message': '[Server Error] Response is none.'}

            print('[Login Server] Send back response to the client:', result)
            try:
                self.socket.send(json.dumps(result).encode('utf-8'))

            except socket.error as e:
                print('[Socket ERROR] Send data to client socket fail:', e)
            except socket.timeout as e:
                print('[Socket ERROR] Send data to socket timeout:', e)
            except Exception as e:
                print('[Socket ERROR] Undefiend error:', e)

            finally:
                self.socket.close()


if __name__ == '__main__':
    ip, port = '127.0.0.1', 10008

    if len(sys.argv) == 3:
        ip, port = sys.argv[1], int(sys.argv[2])
    else:
        print('Usage: python3 {} IP PORT'.format(sys.argv[0]))

    # Create thread lock to handle race condition of app server management
    thread_lock = threading.Lock()

    # Set up APP server management
    app_server_management = AppServerManageMent()

    # Set up Server Monitor
    server_monitor = ServerMonitor(app_server_management, lock=thread_lock, timeout=600)
    server_monitor.start()

    # Set up a socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    print('Starting up on {} port {}'.format(*server_address))
    server_sock.bind(server_address)
    server_sock.listen(20)

    # Receive commands from clients
    while True:
        client_sock, client_address = server_sock.accept()
        print('\nClient connect:', client_address)

        command = None

        try:
            command = client_sock.recv(1024).decode('utf-8')
            print('Command receive:', command, '\n')

        except socket.error as err:
            print('[Socket ERROR] Receive data from client socket fail:', err)
        except socket.timeout as err:
            print('[Socket ERROR] Receive data from socket timeout:', err)
        except Exception as err:
            print('[Socket ERROR] Undefiend error:', err)

        # Create threads to handle commands for each client
        try:
            client_thread = ClientThread(client_sock, client_address, command, app_server_management)
            client_thread.start()

        except Exception as err:
            print('[ERROR] Create thread fail:', err)
            continue
