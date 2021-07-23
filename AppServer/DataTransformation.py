from DataModel import *


def data_to_api_model(data_type=None, data=None):
    api_data = []

    try:
        if data_type == 'users':
            api_data = [user.asdict() for user in data if user]

        elif data_type == 'friends':
            api_data = [friend.asdict() for friend in data if friend]

        elif data_type == 'invites':
            api_data = [invite.asdict() for invite in data if invite]

        elif data_type == 'posts':
            api_data = [post.asdict() for post in data if post]

        elif data_type == 'joins':
            api_data = [join.asdict() for join in data if join]

        elif data_type == 'groups':
            api_data = [group.asdict() for group in data if group]

    except Exception as err:
        print('[ERROR] \'data_to_api_model\' function fail:', err)
        print('[LOG] type = {}, data = {}'.format(data_type, data))

    return api_data


def api_model_to_data(users=None, friends=None, invites=None, posts=None, groups=None, joins=None):
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

        if len(data) == 0:
            data = None

    except Exception as err:
        print('[ERROR] \'api_model_to_data\' function fail:', err)

    return data
