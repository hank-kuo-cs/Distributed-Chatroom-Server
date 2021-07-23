import time
import random
from MessageBroker import *


class User:
    def __init__(self, id=None, token=None, groups=None, app_server_ip=None):
        self.id = id
        self.token = token
        self.app_server_ip = app_server_ip
        self.groups = groups
        self.group_channels = {}
        self.channel_id = 0
        self._run = True

    def end(self):
        self._run = False

    def listen_to_broker(self):
        global thread_lock

        # Subscribe to the own queue channel to get the message from other user
        thread_lock.acquire(timeout=3)

        self.clear()

        conn = receive_message_from_mqserver(user_channel=(self.id, self.channel_id),
                                             group_channels=self.group_channels)

        thread_lock.release()

        while True:
            if not self._run:
                thread_lock.acquire(timeout=3)
                if conn:
                    unsubscribe_to_mqserver(conn, user_channels=(self.id, self.channel_id),
                                            group_channels=self.group_channels)
                thread_lock.release()
                break

    def clear(self):
        global channel_ids

        if self.group_channels:
            for _, id in self.group_channels.items():
                channel_ids.remove(id)
            self.group_channels.clear()

        if self.channel_id > 0:
            if self.channel_id in channel_ids:
                channel_ids.remove(self.channel_id)
                self.channel_id = get_channel_id()

        if self.groups:
            for g in self.groups:
                self.group_channels[g] = get_channel_id()


'''
users: dict
Key: id
Value: User()
information: Store all information of users
'''
users = {}

'''
user_threads: dict
Key: id
Value: Thread()
information: Run one thread for one user
'''
user_threads = {}

'''
group_nums: dict
Key: group
Value: Int (num of login users)
Information: Store how many users login to the group
'''
group_nums = {}

# Handle the manipulating of group nums to avoid race condition
thread_lock = threading.Lock()

channel_ids = []


def get_channel_id():
    global channel_ids

    while True:
        channel_id = random.randint(1, 1000)
        if channel_id not in channel_ids:
            channel_ids.append(channel_id)

            return channel_id


def replace_id_with_token_and_get_serverip(cmd):
    ip = None

    if len(cmd) > 1:
        id = cmd[1]

        if cmd[0] != 'register' and cmd[0] != 'login':
            if cmd[1] in users and users[cmd[1]].token:
                cmd[1]= users[cmd[1]].token

                if cmd[0] != 'logout' and cmd[0] != 'delete':
                    ip = users[id].app_server_ip

                # To check the num of messages are equal to the num of users in the group
                if cmd[0] == 'send-group' and len(cmd) >= 4:
                    if cmd[2] in group_nums:
                        start_group_message_counter()
            else:
                cmd.pop(1)

    return ' '.join(cmd), ip


def register(id):
    if type(id) != str:
        print('[ERROR] \'register\' function has to pass \'str\' argument.')
        exit(0)

    if id not in users:
        users[id] = User(id=id)
    else:
        print('[ERROR] Cannot register the user who already exist in \'users\'')


def logout(id):
    if type(id) != str:
        print('[ERROR] \'logout\' function has to pass \'str\' argument.')
        exit(0)

    if id in users and users[id].token:
        users[id].token, users[id].app_server_ip = None, None

        # Stop the thread of the user
        users[id].end()
        user_threads[id].join(timeout=0.5)

        # Decrease the number of group_nums storing
        if users[id].groups:
            for g in users[id].groups:
                if g in group_nums:
                    group_nums[g] -= 1
                else:
                    print('[ERROR] Group num has not recorded the user')

                if group_nums[g] < 0:
                    print('[ERROR] Group num cannot be less than 0')

        users.pop(id)
        if id in user_threads:
            user_threads.pop(id)


def login(user):
    if type(user) != User:
        print('[ERROR] \'login\' function has to pass \'User\' argument.')
        exit(0)

    # Stop old tasks before logging
    logout(user.id)

    # Start the thread task of the user
    users[user.id] = user
    user_threads[user.id] = threading.Thread(target=users[user.id].listen_to_broker, daemon=True)
    user_threads[user.id].start()

    # Increase the number of group_nums storing
    global group_nums, thread_lock

    thread_lock.acquire(timeout=3)

    if user.groups:
        for g in user.groups:
            if g in group_nums:
                group_nums[g] += 1
            else:
                group_nums[g] = 1

    thread_lock.release()


def delete(id):
    if type(id) != str:
        print('[ERROR] \'delete\' function has to pass \'str\' argument.')
        exit(0)

    # Have to stop the user task
    logout(id)

    # Clean the user data
    if id in users:
        users.pop(id)
        if id in user_threads:
            user_threads.pop(id)


def join_group(group_name, id):
    if type(id) != str and type(group_name) != str:
        print('[ERROR] \'join_group\' function has to pass \'str\' argument.')
        exit(0)

    if id in users and group_name not in users[id].groups:
        user = User(id=id,
                    token=str(users[id].token),
                    groups=list(users[id].groups),
                    app_server_ip=str(users[id].app_server_ip))
        user.groups.append(group_name)

        # Restart the thread task of the user
        users[id].end()
        user_threads[id].join(timeout=0.5)
        login(user)


def send_group(group_name):
    if group_name in group_nums:
        t_start = time.time()

        # To wait for receiving all messages from the group and start next command input
        while True:
            # Receive all messages success
            if group_nums[group_name] == get_group_message_counter():
                break

            # Timeout
            if time.time() - t_start > 3:
                print('[ERROR] Did not get enough messages from the group:', group_name)
                break

    else:
        print('[ERROR] %s was not in the group_nums' % group_name)


def response_handler(response, command, id):
    global thread_lock

    if command and response['status'] == 0:
        try:
            if command[0] == 'register':
                register(command[1])
            if command[0] == 'login':
                login(User(id=command[1],
                           token=response['token'],
                           groups=response['login-group'],
                           app_server_ip=response['app_server_ip']))
            if command[0] == 'logout':
                logout(id)
            if command[0] == 'delete':
                delete(id)
            if command[0] == 'join-group' or command[0] == 'create-group':
                join_group(command[2], id)
            if command[0] == 'send-group':
                send_group(command[2])

        except Exception as e:
            print('[ERROR] Handle the success response fail:', e)

        try:
            sleep_commands = ['login', 'logout', 'delete', 'send', 'send-group', 'join-group', 'create-group']

            if command[0] in sleep_commands:
                thread_lock.acquire(timeout=3)
                thread_lock.release()
                time.sleep(1)

        except Exception as e:
            print('[ERROR] Sleep after handling response fail:', e)

    if 'message' in response:
        print(response['message'])

    if 'invite' in response:
        if len(response['invite']) > 0:
            for l in response['invite']:
                print(l)
        else:
            print('No invitations')

    if 'friend' in response:
        if len(response['friend']) > 0:
            for l in response['friend']:
                print(l)
        else:
            print('No friends')

    if 'post' in response:
        if len(response['post']) > 0:
            for p in response['post']:
                print('{}: {}'.format(p['id'], p['message']))
        else:
            print('No posts')

    if 'group' in response:
        if len(response['group']) > 0:
            for g in response['group']:
                print(g)
        else:
            print('No groups')

