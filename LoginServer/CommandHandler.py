from KeyModule import *
from DataTransformation import *
import time


class Command:
    def __init__(self, type_id, usage_num, usage_message):
        self.type_id = type_id
        self.usage_num = usage_num
        self.usage_message = usage_message
        self.success_message = {'status': 0, 'message': 'Success!'}


commands = {'register': Command(0, 3, 'Usage: register <id> <password>'),
            'login': Command(1, 3, 'Usage: login <id> <password>'),
            'logout': Command(2, 2, 'Usage: logout <user>'),
            'delete': Command(3, 2, 'Usage: delete <user>'),
            'invite': Command(4, 3, 'Usage: invite <user> <id>'),
            'accept-invite': Command(5, 3, 'Usage: accept-invite <user> <id>'),
            'post': Command(6, 3, 'Usage: post <user> <message>'),
            'list-invite': Command(10, 2, 'Usage: list-invite <user>'),
            'list-friend': Command(11, 2, 'Usage: list-friend <user>'),
            'receive-post': Command(12, 2, 'Usage: receive-post <user>'),
            'send': Command(30, 4, 'Usage: send <user> <friend> <message>'),
            'send-group': Command(31, 4, 'Usage: send-group <user> <group> <message>'),
            'create-group': Command(21, 3, 'Usage: create-group <user> <group>'),
            'join-group': Command(22, 3, 'Usage: join-group <user> <group>'),
            'list-group': Command(23, 2, 'Usage: list-group <user>'),
            'list-joined': Command(24, 2, 'Usage: list-joined <user>')}
app_server_management = None


# Command handler
def command_handler(command, management):
    global app_server_management

    app_server_management = management

    c_list = command.split()
    command = commands.get(c_list[0])

    if not command:
        return {'status': 1, 'message': 'Unknown command ' + c_list[0]}

    else:
        # These commands don't have to replace id by token
        # register
        if command == commands['register']:
            result = register(c_list)

        # login
        elif command == commands['login']:
            result = login(c_list)

        # These commands have to replace id by token
        else:
            if len(c_list) < 2 or is_token(c_list[1]) is False:
                return {'status': 1, 'message': 'Not login yet'}

            # logout
            if command == commands['logout']:
                result = logout(c_list)

            # delete
            elif command == commands['delete']:
                result = delete(c_list)

            # other commands but not login
            else:
                return {'status': 1, 'message': 'Not login yet'}

    return result


# Update user last login time
def update_user_last_login(guid):
    # Update the user login time
    if send_sql_command(func='select_last_login_by_guid', keys=['guid'], datas=[guid]):
        if send_sql_command(func='update_last_login',
                            keys=['guid', 'last_login'],
                            datas=[guid, str(int(time.time()))]) is False:
            return {'status': 1, 'message': 'SQL Error'}
    else:
        if send_sql_command(func='insert_last_login',
                            keys=['guid', 'last_login'],
                            datas=[guid, str(int(time.time()))]) is False:
            return {'status': 1, 'message': 'SQL Error'}


def clean_user_last_login(guid):
    if send_sql_command(func='delete_last_login', keys=['guid'], datas=[guid]) is False:
        return {'status': 1, 'message': 'SQL Error'}


# Inspect some situations
def is_login(user):
    # Check this user's login state
    if user.is_login == 0:
        return False
    return True


# Commands
def register(c_list):
    # Check command usage
    if len(c_list) != commands['register'].usage_num:
        return {'status': 1, 'message': commands['register'].usage_message}

    user = send_sql_command(func='select_user_by_id', keys=['id'], datas=[c_list[1]])

    if not user:
        user = User(guid_generaotor(), c_list[1], c_list[2], '', 0)

        if send_sql_command(func='insert_user', keys=['users'], datas=[user]) is False:
            return {'status': 1, 'message': 'SQL Error'}

        return {'status': 0, 'message': 'Success!'}

    user = user[0]

    return {'status': 1, 'message': '%s is already used' % user.id}


def login(c_list):
    # Check command usage
    if len(c_list) != commands['login'].usage_num:
        return {'status': 1, 'message': commands['login'].usage_message}

    user = send_sql_command(func='select_user_by_id', keys=['id'], datas=[c_list[1]])

    if not user or user[0].password != c_list[2]:
        return {'status': 1, 'message': 'No such user or password error'}

    user = user[0]

    if not is_login(user):
        user.token = token_generator()
        user.is_login = 1

        # Update the user login state and token
        if send_sql_command(func='update_user', keys=['users'], datas=[user]) is False:
            return {'status': 1, 'message': 'SQL Error'}

    joins = send_sql_command(func='select_joins_by_guid', keys=['guid'], datas=[user.guid])

    join_list = []

    if joins:
        for j in joins:
            join_list.append(j.groupname)

    # Allocate user to App server
    app_server_ip = app_server_management.allocate_user_to_app_server(user.guid)

    # Update user last login time
    update_user_last_login(user.guid)

    return {'token': user.token, 'status': 0, 'message': 'Success!',
            'login-group': join_list, 'app_server_ip': app_server_ip}


def logout(c_list, monitor_state=False):
    # Check command usage
    if len(c_list) != commands['logout'].usage_num:
        return {'status': 1, 'message': commands['logout'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]]) \
        if not monitor_state else send_sql_command(func='select_user_by_guid', keys=['guid'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    if monitor_state:
        print('[Server Monitor] Logout user {}'.format(user.id))

    user.is_login = 0

    # Update DB USER table
    if send_sql_command(func='update_user', keys=['users'], datas=[user]) is False:
        return {'status': 1, 'message': 'SQL Error'}

    # Remove user from APP Server
    app_server_management.remove_user_from_app_server(user.guid)

    # Clean user last login time
    clean_user_last_login(user.guid)

    return {'status': 0, 'message': 'Bye!'}


def delete(c_list):
    # Check command usage
    if len(c_list) != commands['delete'].usage_num:
        return {'status': 1, 'message': commands['delete'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or is_login(user[0]) is False:
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    if send_sql_command(func='delete_user_by_guid', keys=['guid'], datas=[user.guid]) \
            and send_sql_command(func='delete_friends_by_guid', keys=['guid'], datas=[user.guid]) \
            and send_sql_command(func='delete_friends_by_friend_guid', keys=['friend_guid'], datas=[user.guid]) \
            and send_sql_command(func='delete_invites_by_guid', keys=['guid'], datas=[user.guid]) \
            and send_sql_command(func='delete_invites_by_invite_guid', keys=['invite_guid'], datas=[user.guid]) \
            and send_sql_command(func='delete_posts_by_guid', keys=['guid'], datas=[user.guid]) \
            and send_sql_command(func='delete_joins_by_guid', keys=['guid'], datas=[user.guid]):
        app_server_management.remove_user_from_app_server(user.guid)

        # Clean user last login time
        clean_user_last_login(user.guid)

        return {'status': 0, 'message': 'Success!'}

    return {'status': 1, 'message': 'SQL Error'}
