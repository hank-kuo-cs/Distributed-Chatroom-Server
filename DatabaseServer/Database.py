import sqlite3
from DataModel import *


db_name = 'hw5_0416027.db'


def create_tables():

    try:
        # Create database
        db_connect = sqlite3.connect(db_name)

        # Create Tables
        c = db_connect.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS USER (
               GUID         TEXT PRIMARY KEY    NOT NULL,
               ID           TEXT UNIQUE         NOT NULL,
               PASSWORD     TEXT                NOT NULL,
               TOKEN        TEXT UNIQUE,
               ISLOGIN      BOOLEAN             NOT NULL
               );''')
        c.execute('''CREATE TABLE IF NOT EXISTS FRIEND (
               KEYGUID      TEXT PRIMARY KEY    NOT NULL,
               GUID         TEXT                NOT NULL,
               ID           TEXT                NOT NULL,
               FRIENDGUID   TEXT                NOT NULL,
               FRIENDID     TEXT                NOT NULL,
               REPLY        BOOLEAN
               );''')
        c.execute('''CREATE TABLE IF NOT EXISTS INVITE (
               KEYGUID      TEXT PRIMARY KEY    NOT NULL,
               GUID         TEXT                NOT NULL,
               ID           TEXT                NOT NULL,
               INVITEGUID   TEXT                NOT NULL,
               INVITEID     TEXT                NOT NULL
               );''')
        c.execute('''CREATE TABLE IF NOT EXISTS POST (
               GUID         TEXT                NOT NULL,
               ID           TEXT                NOT NULL,
               POST         TEXT                NOT NULL
               );''')
        c.execute('''CREATE TABLE IF NOT EXISTS USERGROUP (
               GROUPNAME    TEXT UNIQUE         NOT NULL
               );''')
        c.execute('''CREATE TABLE IF NOT EXISTS JOINGROUP (
               GUID         TEXT                NOT NULL,
               GROUPNAME    TEXT                NOT NULL
               );''')
        c.execute('''CREATE TABLE IF NOT EXISTS LASTLOGIN (
               USERGUID     TEXT PRIMARY KEY    NOT NULL,
               LASTLOGIN    TEXT                NOT NULL
               );''')

        db_connect.commit()
        db_connect.close()

        print("Tables created successfully")

    except sqlite3.Error as err:
        print('[ERROR] Create tables fail: ', err)


def sql_object_to_data(db_users=None, db_friends=None, db_invites=None, db_posts=None, db_groups=None, db_joins=None,
                       db_user=None, db_friend=None, db_invite=None, db_post=None, db_group=None, db_join=None):
    if db_users:
        users = []

        for u in db_users:
            user = User(u[0], u[1], u[2], u[3], u[4])
            users.append(user)

        return users

    elif db_friends:
        friends = []

        for f in db_friends:
            friend = Friend(f[0], f[1], f[2], f[3], f[4], f[5])
            friends.append(friend)

        return friends

    elif db_invites:
        invites = []

        for i in db_invites:
            invite = Invite(i[0], i[1], i[2], i[3], i[4])
            invites.append(invite)

        return invites

    elif db_posts:
        posts = []

        for p in db_posts:
            post = Post(p[0], p[1], p[2])
            posts.append(post)

        return posts

    elif db_groups:
        groups = []

        for g in db_groups:
            group = UserGroup(g[0])
            groups.append(group)

        return groups

    elif db_joins:
        joins = []

        for j in db_joins:
            join = JoinGroup(j[0], j[1])
            joins.append(join)

        return joins

    elif db_user:
        return User(db_user[0], db_user[1], db_user[2], db_user[3],
                    db_user[4])

    elif db_friend:
        return Friend(db_friend[0], db_friend[1], db_friend[2], db_friend[3], db_friend[4], db_friend[5])

    elif db_invite:
        return Invite(db_invite[0], db_invite[1], db_invite[2], db_invite[3], db_invite[4])

    elif db_post:
        return Post(db_post[0], db_post[1], db_post[2])

    elif db_group:
        return UserGroup(db_group[0])

    elif db_join:
        return JoinGroup(db_join[0], db_join[1])

    return None


def quotation_handle(s):
    # Because we can't push a string containing quotations(') into the SQL commands
    # We have to transform ' between ''
    # String -> String
    return s.replace('\'', '\'\'')


# User SQL Commands
def select_users():
    # Select all users
    # Return type: [User]

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM USER')

        users = sql_object_to_data(db_users=db_cursor.fetchall())

        db_connect.close()

    except sqlite3.Error as err:
        print('[ERROR] Select all users fail:', err)
        users = None

    return users


def select_user_by_id(id):
    # Select an user with assigned id
    # Return type: User

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM USER WHERE ID = \'%s\'' % quotation_handle(id))
        user = sql_object_to_data(db_user=db_cursor.fetchone())

    except sqlite3.Error as err:
        print('[ERROR] Select an user by id fail:', err)
        user = None

    db_connect.close()

    return user


def select_user_by_token(token):
    # Select an user with assigned token
    # Return type: User

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM USER WHERE TOKEN = \'%s\'' % token)

        user = sql_object_to_data(db_user=db_cursor.fetchone())

        db_connect.close()

    except sqlite3.Error as err:
        print('[ERROR] Select an user by token fail:', err)
        user = None

    return user


def select_user_by_guid(guid):
    # Select an user with assigned guid
    # Return type: User

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM USER WHERE GUID = \'%s\'' % guid)

        user = sql_object_to_data(db_user=db_cursor.fetchone())

        db_connect.close()

    except sqlite3.Error as err:
        print('[ERROR] Select an user by token fail:', err)
        user = None

    return user


def update_user(user):
    # Update a user record
    # Just update its TOKEN and ISLOGIN (Cannot change other values)

    is_update = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('UPDATE USER SET TOKEN = \'%s\', ISLOGIN = %d WHERE GUID = \'%s\''
                      % (user.token, user.is_login, user.guid))

    except sqlite3.Error as err:
        print('[ERROR] Update an user error:', err)
        is_update = False

    db_connect.commit()
    db_connect.close()

    return is_update


def insert_user(user):
    # Insert a user record to the table USER
    # Its ISLOGIN will be set to 0, TOKEN will be set to NULL
    # Because these two values only will be changed when login/logout

    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('INSERT INTO USER (GUID, ID, PASSWORD, TOKEN, ISLOGIN) VALUES (\'%s\', \'%s\', \'%s\', NULL, 0);'
                          % (user.guid, quotation_handle(user.id), quotation_handle(user.password)))

    except sqlite3.Error as err:
        print('[ERROR] Insert an user fail:', err)
        is_insert = False

    db_connect.commit()
    db_connect.close()

    return is_insert


def delete_user_by_guid(guid):
    # Delete an user record with assigned guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM USER WHERE GUID = \'%s\'' % guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete an user by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


# Invite SQL Commands
def insert_invite(invite):
    # Insert a invite record to the table INVITE
    # A invite B -> invite guid will be A's guid + B's guid

    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute(
            'INSERT INTO INVITE (KEYGUID, GUID, ID, INVITEGUID, INVITEID) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\');'
            % (invite.key_guid, invite.guid, quotation_handle(invite.id), invite.invite_guid, quotation_handle(invite.invite_id)))

    except sqlite3.Error as err:
        is_insert = False
        print('[ERROR] Insert an invite fail:', err)

    db_connect.commit()
    db_connect.close()

    return is_insert


def select_invite_by_key_guid(key_guid):
    # Select an invite record with assigned key_guid
    # Return type: Invite
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM INVITE WHERE KEYGUID = \'%s\'' % key_guid)

        invite = sql_object_to_data(db_invite=db_cursor.fetchone())

    except sqlite3.Error as err:
        print('[ERROR] Select an invite by key_guid fail:', err)
        invite = None

    db_connect.close()

    return invite


def select_invites_by_invite_guid(invite_guid):
    # Select invite records with assigned invite_guid
    # Means that check who invites you
    # Return type: [Invite]
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM INVITE WHERE INVITEGUID = \'%s\'' % invite_guid)

        invites = sql_object_to_data(db_invites=db_cursor.fetchall())

    except sqlite3.Error as err:
        print('[ERROR] Select invites by invite_guid fail:', err)
        invites = []

    db_connect.close()

    return invites


def select_invites_by_guid(guid):
    # Select invite records with assigned guid
    # Means that check who you invite
    # Return type: [Invite]

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM INVITE WHERE GUID = \'%s\'' % guid)

        invites = sql_object_to_data(db_invites=db_cursor.fetchall())

    except sqlite3.Error as err:
        print('[ERROR] Select invites by guid fail:', err)
        invites = []

    db_connect.close()

    return invites


def delete_invite_by_key_guid(key_guid):
    # Delete an invite record with assigned key_guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM INVITE WHERE KEYGUID = \'%s\'' % key_guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete an invite by key_guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


def delete_invites_by_guid(guid):
    # Delete an invite record with assigned key_guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM INVITE WHERE GUID = \'%s\'' % guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete invites by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


def delete_invites_by_invite_guid(invite_guid):
    # Delete an invite record with assigned key_guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM INVITE WHERE INVITEGUID = \'%s\'' % invite_guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete invites by invite_guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


# Friend SQL Commands
def insert_friend(friend):
    # Insert a invite record to the table INVITE
    # A invite B -> invite guid will be A's guid + B's guid

    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute(
            'INSERT INTO FRIEND (KEYGUID, GUID, ID, FRIENDGUID, FRIENDID, REPLY) VALUES (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', %d);'
            % (friend.key_guid, friend.guid, quotation_handle(friend.id), friend.friend_guid, quotation_handle(friend.friend_id), friend.reply))

    except sqlite3.Error as err:
        print('[ERROR] Insert an invite fail:', err)
        is_insert = False

    db_connect.commit()
    db_connect.close()

    return is_insert


def select_friend_by_key_guid(key_guid):
    # Select friend records with assigned guid
    # Return type: Friend

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM FRIEND WHERE KEYGUID = \'%s\'' % key_guid)

        friend = sql_object_to_data(db_friend=db_cursor.fetchone())

    except sqlite3.Error as err:
        print('[ERROR] Select a friend record by key_guid fail:', err)
        friend = None

    db_connect.close()

    return friend


def select_friends_by_guid(guid):
    # Select friend records with assigned guid
    # Return type: [Friend]

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM FRIEND WHERE GUID = \'%s\'' % guid)

        friends = sql_object_to_data(db_friends=db_cursor.fetchall())

    except sqlite3.Error as err:
        print('[ERROR] Select friend records by guid fail:', err)
        friends = []

    db_connect.close()

    return friends


def update_friend_reply(id, friend_id, reply):
    # Update a friend record
    # Just update its REPLY (Cannot change other values)

    is_update = True
    if type(id) != str or type(friend_id) != str or type(reply) != int:
        print('[ERROR] Update an friend error: type of argument fault.')
        return False

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('UPDATE FRIEND SET REPLY = %d WHERE ID = \'%s\' AND FRIENDID = \'%s\''
                          % (reply, quotation_handle(id), quotation_handle(friend_id)))

    except sqlite3.Error as err:
        print('[ERROR] Update an friend error:', err)
        is_update = False

    db_connect.commit()
    db_connect.close()

    return is_update


def delete_friend_by_key_guid(key_guid):
    # Delete a friend record with assigned key_guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM FRIEND WHERE KEYGUID = \'%s\'' % key_guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete a friend record by key_guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


def delete_friends_by_guid(guid):
    # Delete friend records with assigned guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM FRIEND WHERE GUID = \'%s\'' % guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete friend records by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


def delete_friends_by_friend_guid(friend_guid):
    # Delete friend records with assigned friend_guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM FRIEND WHERE FRIENDGUID = \'%s\'' % friend_guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete friend records by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


# Post SQL Commands
def insert_post(post):
    # insert a post record to the table POST

    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute(
            'INSERT INTO POST (GUID, ID, POST) VALUES (\'%s\', \'%s\', \'%s\');'
            % (post.guid, quotation_handle(post.id), quotation_handle(post.post)))

    except sqlite3.Error as err:
        is_insert = False
        print('[ERROR] Insert a post record fail:', err)

    db_connect.commit()
    db_connect.close()

    return is_insert


def select_posts_by_friends(friends):

    # Select post records with assigned guids
    # Means that return all posts of any guid from 'guids' list
    # Return type: [Post]

    post_list = []

    if friends:

        db_connect = sqlite3.connect(db_name)
        db_cursor = db_connect.cursor()

        try:
            for friend in friends:
                if friend:
                    db_cursor.execute('SELECT * FROM POST WHERE GUID = \'%s\'' % friend.friend_guid)

                    posts = sql_object_to_data(db_posts=db_cursor.fetchall())

                    if posts:
                        post_list.extend(posts)

        except sqlite3.Error as err:
            print('[ERROR] Select post records by friends fail:', err)
            post_list = []

        db_connect.close()

    return post_list


def delete_posts_by_guid(guid):
    # Delete post records with assigned guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM POST WHERE GUID = \'%s\'' % guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete post records by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


# Join SQL Commands
def select_join_by_guid_groupname(guid, groupname):
    # Check the user whether in the group
    # Return type: Join
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()
    try:
        db_cursor.execute('SELECT * FROM JOINGROUP WHERE GUID = \'%s\' AND GROUPNAME = \'%s\'' % (guid, quotation_handle(groupname)))
        join = sql_object_to_data(db_join=db_cursor.fetchone())

    except sqlite3.Error as err:
        print('[ERROR] Select join records by guid fail:', err)
        join = None

    db_connect.commit()
    db_connect.close()

    return join


def select_joins_by_guid(guid):
    # Find all groups the user has joined
    # Return type: [Join]
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM JOINGROUP WHERE GUID = \'%s\'' % guid)
        joins = sql_object_to_data(db_joins=db_cursor.fetchall())

    except sqlite3.Error as err:
        print('[ERROR] Select join records by guid fail:', err)
        joins = []

    db_connect.commit()
    db_connect.close()

    return joins


def insert_join(join):
    # insert a post record to the table POST
    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute(
            'INSERT INTO JOINGROUP (GUID, GROUPNAME) VALUES (\'%s\', \'%s\');'
            % (join.guid, quotation_handle(join.groupname)))

    except sqlite3.Error as err:
        is_insert = False
        print('[ERROR] Insert a join record fail:', err)

    db_connect.commit()
    db_connect.close()

    return is_insert


def delete_joins_by_guid(guid):
    # Delete join records with assigned guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM JOINGROUP WHERE GUID = \'%s\'' % guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete join records by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete


# Group SQL Commands
def select_group_by_groupname(groupname):
    # Check the name whether exists in the USERGROUP db
    # Return type: UserGroup
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM USERGROUP WHERE GROUPNAME = \'%s\'' % quotation_handle(groupname))
        group = sql_object_to_data(db_group=db_cursor.fetchone())

    except sqlite3.Error as err:
        print('[ERROR] Select usergroup record by name fail:', err)
        group = None

    db_connect.commit()
    db_connect.close()

    return group


def select_all_groups():
    # Find all groups the user has joined
    # Return type: [Group]
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM USERGROUP')
        groups = sql_object_to_data(db_groups=db_cursor.fetchall())

    except sqlite3.Error as err:
        print('[ERROR] Select all group records fail:', err)
        groups = []

    db_connect.commit()
    db_connect.close()

    return groups


def insert_group(group):
    # Insert a group to db
    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute(
            'INSERT INTO USERGROUP (GROUPNAME) VALUES (\'%s\');'
            % (quotation_handle(group.groupname)))

    except sqlite3.Error as err:
        is_insert = False
        print('[ERROR] Insert a usergroup record fail:', err)
        print('[LOG] group: type = {}, data = {}'.format(type(group), group))

    db_connect.commit()
    db_connect.close()

    return is_insert


# LastLogin SQL Commands
def select_last_login_by_guid(guid):
    # Find the last login time with the user guid
    # Return type: str
    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('SELECT * FROM LASTLOGIN WHERE USERGUID = \'%s\'' % guid)
        data = db_cursor.fetchone()
        last_login = data[1] if data else None

    except sqlite3.Error as err:
        print('[ERROR] Select last_login records by guid fail:', err)
        last_login = None

    db_connect.commit()
    db_connect.close()

    return last_login


def insert_last_login(guid, last_login):
    # Insert a last login to db
    is_insert = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute(
            'INSERT INTO LASTLOGIN (USERGUID, LASTLOGIN) VALUES (\'%s\', \'%s\');'
            % (guid, last_login))

    except sqlite3.Error as err:
        is_insert = False
        print('[ERROR] Insert a last_login record fail:', err)

    db_connect.commit()
    db_connect.close()

    return is_insert


def update_last_login(guid, last_login):
    # Just update its REPLY (Cannot change other values)

    is_update = True
    if type(guid) != str or type(last_login) != str:
        print('[ERROR] Update an last_login error: type of argument fault.')
        return False

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('UPDATE LASTLOGIN SET LASTLOGIN = \'%s\' WHERE USERGUID = \'%s\''
                          % (last_login, guid))

    except sqlite3.Error as err:
        print('[ERROR] Update an last_login error:', err)
        is_update = False

    db_connect.commit()
    db_connect.close()

    return is_update


def delete_last_login(guid):
    # Delete last_login records with assigned guid

    is_delete = True

    db_connect = sqlite3.connect(db_name)
    db_cursor = db_connect.cursor()

    try:
        db_cursor.execute('DELETE FROM LASTLOGIN WHERE USERGUID = \'%s\'' % guid)

    except sqlite3.Error as err:
        print('[ERROR] Delete last_login records by guid fail:', err)
        is_delete = False

    db_connect.commit()
    db_connect.close()

    return is_delete
