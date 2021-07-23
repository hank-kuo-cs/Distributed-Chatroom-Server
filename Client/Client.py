import os
import sys
import time
from SocketConnector import SocketConnector
from ResponseHandler import response_handler, replace_id_with_token_and_get_serverip


if __name__ == '__main__':
    login_server_ip, login_server_port = '127.0.0.1', 10006

    if len(sys.argv) == 3:
        login_server_ip, login_server_port = sys.argv[1], int(sys.argv[2])
    else:
        print('Usage: python3 {} IP PORT'.format(sys.argv[0]))

    socket_connector = SocketConnector()

    # Receive the user input
    while True:
        user_input = sys.stdin.readline()

        if user_input == 'exit' + os.linesep:
            time.sleep(0.5)
            exit(0)

        if user_input != os.linesep:
            cmd = user_input.split()

            user_id = cmd[1] if cmd and len(cmd) > 1 else None

            if cmd:
                command, ip = replace_id_with_token_and_get_serverip(cmd)

                port = 10008 if ip else login_server_port
                ip = ip if ip else login_server_ip

                # Socket connect to the server and get the response
                socket_connector.connect_to_server(ip=ip, port=port)

                socket_connector.send_command_to_server(command)

                response = socket_connector.receive_response_from_server()

                # Handle the response
                if response:
                    response_handler(response, command.split(), user_id)
                else:
                    print('Response is None, check the server')
