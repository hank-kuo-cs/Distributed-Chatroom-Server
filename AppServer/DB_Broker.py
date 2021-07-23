import json
import socket
from DataTransformation import *


def send_sql_command(func, keys, datas):
    if type(func) != str or type(keys) != list or type(datas) != list:
        print('[ERROR] Types of arguments are not correct')
        print('Type: func = {}, keys = {}, datas = {}'.format(type(func), type(keys), type(datas)))
        return

    sql_command = dict(func=func)

    if len(keys) > 0 and keys[0] in type_enum:
        api_data = data_to_api_model(data_type=keys[0], data=datas)
        sql_command[keys[0]] = api_data

    else:
        if len(keys) != len(datas):
            print('[ERROR] keys does not match datas')

        for i, key in enumerate(keys):
            sql_command[key] = datas[i]

    return send_command_to_db_server(sql_command)


def send_command_to_db_server(sql_command):
    db_server_ip, db_server_port = '3.84.189.214', 10009

    response = None

    print('\tSend sql command to db server:', sql_command)

    # Set up the socket to connect to the server
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((db_server_ip, db_server_port))
        s.send(json.dumps(sql_command).encode())
        response = json.loads(s.recv(8192).decode())
        s.close()

    except Exception as e:
        print('[ERROR] send sql socket set up fail:', e)

    print('\tDB Server response:', response)

    return db_server_response_handler(response)


def db_server_response_handler(db_server_response):
    try:
        if db_server_response['status'] == 0:
            if db_server_response['type'] == 'Boolean' or db_server_response['type'] == 'str':
                return db_server_response['data'][0]

            elif db_server_response['type'] == 'users':
                return api_model_to_data(users=db_server_response['data'])

            elif db_server_response['type'] == 'friends':
                return api_model_to_data(friends=db_server_response['data'])

            elif db_server_response['type'] == 'invites':
                return api_model_to_data(invites=db_server_response['data'])

            elif db_server_response['type'] == 'posts':
                return api_model_to_data(posts=db_server_response['data'])

            elif db_server_response['type'] == 'groups':
                return api_model_to_data(groups=db_server_response['data'])

            elif db_server_response['type'] == 'joins':
                return api_model_to_data(joins=db_server_response['data'])
            else:
                print('[ERROR] DB server response type is not defined:', db_server_response['type'])

        else:
            print('[ERROR] DB server response error, status =', db_server_response['status'])

    except Exception as err:
        print('[ERROR] Handle response from db server fail:', err)

    return None
