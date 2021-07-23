class User:
    def __init__(self, guid=None, id=None, password=None, token=None, is_login=None, user_dict=None):
        self.guid = guid
        self.id = id
        self.password = password
        self.token = token
        self.is_login = is_login

        if user_dict:
            self.guid = user_dict['guid']
            self.id = user_dict['id']
            self.password = user_dict['password']
            self.token = user_dict['token']
            self.is_login = user_dict['is_login']

    def asdict(self):
        return {'guid': self.guid,
                'id': self.id,
                'password': self.password,
                'token': self.token,
                'is_login': self.is_login}


class Friend:
    def __init__(self, key_guid=None, guid=None, id=None, friend_guid=None, friend_id=None, reply=None, friend_dict=None):
        self.key_guid = key_guid
        self.guid = guid
        self.id = id
        self.friend_guid = friend_guid
        self.friend_id = friend_id
        self.reply = reply

        if friend_dict:
            self.key_guid = friend_dict['key_guid']
            self.guid = friend_dict['guid']
            self.id = friend_dict['id']
            self.friend_guid = friend_dict['friend_guid']
            self.friend_id = friend_dict['friend_id']
            self.reply = friend_dict['reply']

    def asdict(self):
        return {'key_guid': self.key_guid,
                'guid': self.guid,
                'id': self.id,
                'friend_guid': self.friend_guid,
                'friend_id': self.friend_id,
                'reply': self.reply}


class Invite:
    def __init__(self, key_guid=None, guid=None, id=None, invite_guid=None, invite_id=None, invite_dict=None):
        self.key_guid = key_guid
        self.guid = guid
        self.id = id
        self.invite_guid = invite_guid
        self.invite_id = invite_id

        if invite_dict:
            self.key_guid = invite_dict['key_guid']
            self.guid = invite_dict['guid']
            self.id = invite_dict['id']
            self.invite_guid = invite_dict['invite_guid']
            self.invite_id = invite_dict['invite_id']

    def asdict(self):
        return {'key_guid': self.key_guid,
                'guid': self.guid,
                'id': self.id,
                'invite_guid': self.invite_guid,
                'invite_id': self.invite_id}


class Post:
    def __init__(self, guid=None, id=None, post=None, post_dict=None):
        self.guid = guid
        self.id = id
        self.post = post

        if post_dict:
            self.guid = post_dict['guid']
            self.id = post_dict['id']
            self.post = post_dict['post']

    def asdict(self):
        return {'guid': self.guid,
                'id': self.id,
                'post': self.post}


class JoinGroup:
    def __init__(self, guid=None, groupname=None, join_dict=None):
        self.guid = guid
        self.groupname = groupname

        if join_dict:
            self.guid = join_dict['guid']
            self.groupname = join_dict['groupname']

    def asdict(self):
        return {'guid': self.guid,
                'groupname': self.groupname}


class UserGroup:
    def __init__(self, groupname=None, group_dict=None):
        self.groupname = groupname

        if group_dict:
            self.groupname = group_dict['groupname']

    def asdict(self):
        return {'groupname': self.groupname}
