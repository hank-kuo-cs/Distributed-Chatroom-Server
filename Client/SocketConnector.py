import json
import socket


class SocketConnector:
    def __init__(self):
        self.socket = None
        self.command = ''

    def connect_to_server(self, ip, port):
        if port < 10000 or port > 20000:
            print('[Socket Error] You have to set port 10000 ~ 20000')
            return
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))

        except socket.error as e:
            print('[Socket Error] Connect socket ip = {}, port = {} fail:'.format(ip, port), e)

        except Exception as e:
            print('[Socket Error] Undefined error:', e)

    def send_command_to_server(self, command):
        if type(command) != str:
            print('[Socket Error] Type of command is not \'str\' but', type(command))
            return

        self.command = command
        self.socket.settimeout(0.1)

        try:
            self.socket.send(self.command.encode())

        except socket.timeout:
            print('[Socket Error] Send command timeout')

        except socket.error as e:
            print('[Socket Error] Send command fail:', e)

        except Exception as e:
            print('[Socket Error] Undefined error:', e)

    def receive_response_from_server(self):
        if self.command.split()[0] != 'login':
            self.socket.settimeout(10)   # Prevent the login server or app server not send the response
        else:
            self.socket.settimeout(180)  # If the login server has to launch new app server, we have to wait a moment

        response = None

        try:
            response = json.loads(self.socket.recv(4096).decode())

        except socket.timeout:
            print('[Socket Error] Receive response timeout')

        except socket.error as e:
            print('[Socket Error] Receive response fail:', e)

        except Exception as e:
            print('[Socket Error] Undefined error:', e)

        finally:
            self.socket.close()
            if response:
                return response
