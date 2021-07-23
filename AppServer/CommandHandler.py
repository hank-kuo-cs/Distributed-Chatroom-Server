import time
from KeyModule import *
from MessageBroker import *
from DataTransformation import *


class Command:
    def __init__(self, type_id, usage_num, usage_message, success_message):
        self.type_id = type_id
        self.usage_num = usage_num
        self.usage_message = usage_message
        self.success_message = {'status': 0, 'message': 'Success!'}


success_message = {'status': 0, 'message': 'Success!'}
commands = {'register': Command(0, 3, 'Usage: register <id> <password>', 'register: Success!'),
            'login': Command(1, 3, 'Usage: login <id> <password>', 'login: Success!'),
            'logout': Command(2, 2, 'Usage: logout <user>', 'logout: Success!'),
            'delete': Command(3, 2, 'Usage: delete <user>', 'delete: Success!'),
            'invite': Command(4, 3, 'Usage: invite <user> <id>', 'invite: Success!'),
            'accept-invite': Command(5, 3, 'Usage: accept-invite <user> <id>', 'accept-invite: Success!'),
            'post': Command(6, 3, 'Usage: post <user> <message>', 'post: Success!'),
            'list-invite': Command(10, 2, 'Usage: list-invite <user>', ''),
            'list-friend': Command(11, 2, 'Usage: list-friend <user>', ''),
            'receive-post': Command(12, 2, 'Usage: receive-post <user>', ''),
            'send': Command(30, 4, 'Usage: send <user> <friend> <message>', 'Success!'),
            'send-group': Command(31, 4, 'Usage: send-group <user> <group> <message>', 'Success!'),
            'create-group': Command(21, 3, 'Usage: create-group <user> <group>', 'Success!'),
            'join-group': Command(22, 3, 'Usage: join-group <user> <group>', 'Success!'),
            'list-group': Command(23, 2, 'Usage: list-group <user>', ''),
            'list-joined': Command(24, 2, 'Usage: list-joined <user>', '')}


# Update last login time of the user
def update_user_last_login(token):
    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[token])

    if user and is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    guid = user[0].guid

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


# Command handle
def command_handler(command):
    c_list = command.split()
    command = commands.get(c_list[0])

    result = {}

    if not command:
        return {'status': 1, 'message': 'Unknown command ' + c_list[0]}

    else:
        # APP Server do not handle login, logout, register, delete
        if 0 <= command.type_id <= 3:
            return {'status': 1, 'message': 'APP Server does not deal \'{}\''.format(c_list[0])}

        if len(c_list) < 2 or is_token(c_list[1]) is False:
            return {'status': 1, 'message': 'Not login yet'}

        # Update the user last login time
        update_user_last_login(c_list[1])

        # invite
        if command == commands['invite']:
            result = invite(c_list)

        # accept-invite
        elif command == commands['accept-invite']:
            result = accept_invite(c_list)

        # post
        elif command == commands['post']:
            result = post(c_list)

        # receive-post
        elif command == commands['receive-post']:
            result = receive_post(c_list)

        # list-invite
        elif command == commands['list-invite']:
            result = list_invite(c_list)

        # list-friend
        elif command == commands['list-friend']:
            result = list_friend(c_list)

        # create-group
        elif command == commands['create-group']:
            result = create_group(c_list)

        # list-group
        elif command == commands['list-group']:
            result = list_group(c_list)

        # list-joined
        elif command == commands['list-joined']:
            result = list_joined(c_list)

        # join-group
        elif command == commands['join-group']:
            result = join_group(c_list)

        # send
        elif command == commands['send']:
            result = send(c_list)

        # send-group
        elif command == commands['send-group']:
            result = send_group(c_list)

    return result


# Inspect some situations
def is_login(user):
    # Check this user's login state
    if user.is_login == 0:
        return False
    return True


def is_friend(user1, user2):
    # Check these two users' friend state
    if not send_sql_command(func='select_friend_by_key_guid', keys=['key_guid'], datas=[(user1.guid + user2.guid)]) \
            and not send_sql_command(func='select_friend_by_key_guid', keys=['key_guid'], datas=[(user2.guid + user1.guid)]):
        return False

    return True


def is_invite(user1, user2):
    # Check whether user1 invite user2
    if not send_sql_command(func='select_invite_by_key_guid', keys=['key_guid'], datas=[(user1.guid + user2.guid)]):
        return False

    return True


# Commands
def invite(c_list):
    # Check command usage
    if len(c_list) != commands['invite'].usage_num:
        return {'status': 1, 'message': commands['invite'].usage_message}

    token = c_list[1]
    invite_id = c_list[2]

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[token])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    invite_user = send_sql_command(func='select_user_by_id', keys=['id'], datas=[invite_id])

    if not invite_user:
        return {'status': 1, 'message': '%s does not exist' % invite_id}

    invite_user = invite_user[0]

    if user.guid == invite_user.guid:
        return {'status': 1, 'message': 'You cannot invite yourself'}

    if is_friend(user, invite_user):
        return {'status': 1, 'message': '%s is already your friend' % invite_user.id}

    if is_invite(user, invite_user):
        return {'status': 1, 'message': 'Already invited'}

    if is_invite(invite_user, user):
        return {'status': 1, 'message': '%s has invited you' % invite_user.id}

    # Invite success
    invite = Invite(user.guid+invite_user.guid, user.guid, user.id, invite_user.guid, invite_user.id)

    # Insert a record to DB INVITE table
    if send_sql_command(func='insert_invite', keys=['invites'], datas=[invite]) is False:
        return {'status': 1, 'message': 'SQL Error'}

    return {'status': 0, 'message': 'Success!'}


def accept_invite(c_list):
    # Check command usage
    if len(c_list) != commands['accept-invite'].usage_num:
        return {'status': 1, 'message': commands['accept-invite'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    user_who_invite = send_sql_command(func='select_user_by_id', keys=['id'], datas=[c_list[2]])

    if not user_who_invite or not is_invite(user_who_invite[0], user):
        return {'status': 1, 'message': '%s did not invite you' % c_list[2]}

    user_who_invite = user_who_invite[0]

    # Accept invite success
    key_guid = user_who_invite.guid + user.guid

    if send_sql_command(func='delete_invite_by_key_guid', keys=['key_guid'], datas=[key_guid]) is False:
        return {'status': 1, 'message': 'SQL Error'}

    if send_sql_command(func='insert_friend', keys=['friends'], datas=[Friend(key_guid, user_who_invite.guid, user_who_invite.id, user.guid, user.id, 0)]) is False:
        return {'status': 1, 'message': 'SQL Error'}

    if send_sql_command(func='insert_friend', keys=['friends'], datas=[Friend(user.guid + user_who_invite.guid, user.guid, user.id, user_who_invite.guid, user_who_invite.id, 0)]) is False:
        return {'status': 1, 'message': 'SQL Error'}

    return {'status': 0, 'message': 'Success!'}


def post(c_list):
    # Check command usage
    if len(c_list) < commands['post'].usage_num:
        return {'status': 1, 'message': commands['post'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or is_login(user[0]) is False:
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    if send_sql_command(func='insert_post', keys=['posts'], datas=[Post(user.guid, user.id, ' '.join(c_list[2:]))]) is False:
        return {'status': 1, 'message': 'SQL Error'}

    return {'status': 0, 'message': 'Success!'}


def receive_post(c_list):
    # Check command usage
    if len(c_list) != commands['receive-post'].usage_num:
        return {'status': 1, 'message': commands['receive-post'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or is_login(user[0]) is False:
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    post_list = []

    friends = send_sql_command(func='select_friends_by_guid', keys=['guid'], datas=[user.guid])
    if type(friends) != list:
        friends = [friends]

    posts = send_sql_command(func='select_posts_by_friends', keys=['friends'], datas=friends)

    if posts:
        for post in posts:
            post_list.append({'id': post.id, 'message': post.post})

    return {'status': 0, 'post': post_list}


def list_invite(c_list):
    # Check command usage
    if len(c_list) != commands['list-invite'].usage_num:
        return {'status': 1, 'message': commands['list-invite'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]
    invite_list = []

    invites = send_sql_command(func='select_invites_by_invite_guid', keys=['invite_guid'], datas=[user.guid])

    if invites:
        for invite in invites:
            invite_list.append(invite.id)

    return {'status': 0, 'invite': invite_list}


def list_friend(c_list):
    # Check command usage
    if len(c_list) != commands['list-friend'].usage_num:
        return {'status': 1, 'message': commands['list-friend'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]
    friend_list = []

    friends = send_sql_command(func='select_friends_by_guid', keys=['guid'], datas=[user.guid])

    if friends:
        for friend in friends:
            friend_list.append(friend.friend_id)

    return {'status': 0, 'friend': friend_list}


def create_group(c_list):
    if len(c_list) != commands['create-group'].usage_num:
        return {'status': 1, 'message': commands['create-group'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    group = send_sql_command(func='select_group_by_groupname', keys=['groupname'], datas=[c_list[2]])

    if group:
        return {'status': 1, 'message': '%s already exist' % c_list[2]}

    if not send_sql_command(func='insert_group', keys=['groups'], datas=[UserGroup(c_list[2])]) or\
        not send_sql_command(func='insert_join', keys=['joins'], datas=[JoinGroup(user.guid, c_list[2])]):
        return {'status': 1, 'message': 'SQL Error'}

    return commands['create-group'].success_message


def list_group(c_list):
    if len(c_list) != commands['list-group'].usage_num:
        return {'status': 1, 'message': commands['list-group'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    groups = send_sql_command(func='select_all_groups', keys=[], datas=[])

    group_list = []

    if groups:
        for g in groups:
            group_list.append(g.groupname)

    return {'status': 0, 'group': group_list}


def list_joined(c_list):
    if len(c_list) != commands['list-joined'].usage_num:
        return {'status': 1, 'message': commands['list-joined'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    joins = send_sql_command(func='select_joins_by_guid', keys=['guid'], datas=[user.guid])

    join_list = []

    if joins:
        for j in joins:
            join_list.append(j.groupname)

    return {'status': 0, 'group': join_list}


def join_group(c_list):
    if len(c_list) != commands['join-group'].usage_num:
        return {'status': 1, 'message': commands['join-group'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    group = send_sql_command(func='select_group_by_groupname', keys=['groupname'], datas=[c_list[2]])

    if not group:
        return {'status': 1, 'message': '%s does not exist' % c_list[2]}

    join = send_sql_command(func='select_join_by_guid_groupname', keys=['guid', 'groupname'], datas=[user.guid, c_list[2]])

    if join:
        return {'status': 1, 'message': 'Already a member of %s' % c_list[2]}

    if not send_sql_command(func='insert_join', keys=['joins'], datas=[JoinGroup(user.guid, c_list[2])]):
        return {'status': 1, 'message': 'SQL Error'}

    return commands['join-group'].success_message


def send(c_list):
    # Check command usage
    if len(c_list) < commands['send'].usage_num:
        return {'status': 1, 'message': commands['send'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]

    user_friend = send_sql_command(func='select_user_by_id', keys=['id'], datas=[c_list[2]])

    if not user_friend:
        return {'status': 1, 'message': 'No such user exist'}
    else:
        user_friend = user_friend[0]

        if not is_friend(user, user_friend):
            return {'status': 1, 'message': '%s is not your friend' % c_list[2]}

        if not is_login(user_friend):
            return {'status': 1, 'message': '%s is not online' % c_list[2]}

        message = '<<<' + user.id + '->' + c_list[2] + ': ' + ' '.join(c_list[3:]) + '>>>'
        send_to_queue(msg=message, id=user.id, friend_id=user_friend.id)
        channel_id = random.randint(1001, 8000)
        conn = receive_from_queue(id=user.id, friend_id=user_friend.id, channel_id=channel_id)

        key_guid = user_friend.guid + user.guid
        t_start = time.time()

        while True:

            friend = send_sql_command(func='select_friend_by_key_guid', keys=['key_guid'], datas=[key_guid])[0]

            if friend.reply == 1:
                if not send_sql_command(func='update_friend_reply',
                                        keys=['id', 'friend_id', 'reply'],
                                        datas=[friend.id, friend.friend_id, 0]):
                    print({'status': 1, 'message': 'SQL Error'})

                unsubscribe_from_queue(conn, (user_friend.id + '.reply.' + user.id), channel_id=channel_id)
                return commands['send'].success_message

            if time.time() - t_start > 3:
                unsubscribe_from_queue(conn, (user_friend.id + '.reply.' + user.id), channel_id=channel_id)
                break

        # Delete the message due to timeout
        channel_friend_id = random.randint(1001, 8000)
        conn_friend = receive_from_queue(friend_id=user_friend.id, channel_id=channel_friend_id)

        unsubscribe_from_queue(conn_friend, user_friend.id, channel_id=channel_friend_id)
        if not send_sql_command(func='update_friend_reply',
                                keys=['id', 'friend_id', 'reply'],
                                datas=[friend.id, friend.friend_id, 0]):
            print({'status': 1, 'message': 'SQL Error'})

        return {'status': 1, 'message': '%s is not online' % c_list[2]}


def send_group(c_list):
    if len(c_list) < commands['send-group'].usage_num:
        return {'status': 1, 'message': commands['send-group'].usage_message}

    user = send_sql_command(func='select_user_by_token', keys=['token'], datas=[c_list[1]])

    if not user or not is_login(user[0]):
        return {'status': 1, 'message': 'Not login yet'}

    user = user[0]
    group = send_sql_command(func='select_group_by_groupname', keys=['groupname'], datas=[c_list[2]])

    if not group:
        return {'status': 1, 'message': 'No such group exist'}

    join = send_sql_command(func='select_join_by_guid_groupname', keys=['guid', 'groupname'], datas=[user.guid, c_list[2]])

    if not join:
        return {'status': 1, 'message': 'You are not the member of %s' % c_list[2]}

    message = '<<<' + user.id + '->GROUP<' + c_list[2] + '>: ' + ' '.join(c_list[3:]) + '>>>'

    send_to_topic(msg=message, id=user.id, group_name=c_list[2])

    return commands['send-group'].success_message
