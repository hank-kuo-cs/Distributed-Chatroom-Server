from DataModel import *


def data_to_api_model(data_type=None, data=None):
    data_type_enum = ['users', 'friends', 'invites', 'posts', 'joins', 'groups', 'Boolean', 'str']
    response = {'status': 1, 'type': 'ERROR', 'data': []}

    try:
        if data_type in data_type_enum:
            response['type'] = data_type
            response['status'] = 0

        if (type(data) == list and len(data) > 0) or data_type == 'Boolean' or data_type == 'str':
            if data_type == 'users':
                response['data'] = [user.asdict() for user in data if user]

            elif data_type == 'friends':
                response['data'] = [friend.asdict() for friend in data if friend]

            elif data_type == 'invites':
                response['data'] = [invite.asdict() for invite in data if invite]

            elif data_type == 'posts':
                response['data'] = [post.asdict() for post in data if post]

            elif data_type == 'joins':
                response['data'] = [join.asdict() for join in data if join]

            elif data_type == 'groups':
                response['data'] = [group.asdict() for group in data if group]

            elif data_type == 'Boolean':
                response['data'].append(data)

            elif data_type == 'str':
                response['data'].append(data)

    except Exception as err:
        print('[ERROR] \'data_to_api_model\' function fail:', err)

    return response


def api_model_to_data(users=None, friends=None, invites=None, posts=None, joins=None, groups=None):
    data = []

    try:
        if users:
            for user in users:
                data.append(User(user_dict=user))

        if friends:
            for friend in friends:
                data.append(Friend(friend_dict=friend))

        if invites:
            for invite in invites:
                data.append(Invite(invite_dict=invite))

        if posts:
            for post in posts:
                data.append(Post(post_dict=post))

        if joins:
            for join in joins:
                data.append(JoinGroup(join_dict=join))

        if groups:
            for group in groups:
                data.append(UserGroup(group_dict=group))

        if len(data) == 1:
            data = data[0]

        elif len(data) == 0:
            data = None

    except Exception as err:
        print('[ERROR] \'api_model_to_data\' function fail:', err)

    return data
