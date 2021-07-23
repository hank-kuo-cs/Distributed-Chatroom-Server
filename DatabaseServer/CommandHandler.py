from Database import *
from DataTransformation import *


def command_handler(command):
    if type(command) != dict:
        print('[ERROR] Command type is not dict')
        return

    if 'func' in command:
        f = command['func']

        # User
        if f == 'select_users':
            return data_to_api_model(data=select_users(), data_type='users')

        if f == 'select_user_by_id':
            return data_to_api_model(data=[select_user_by_id(command['id'])], data_type='users')

        if f == 'select_user_by_token':
            return data_to_api_model(data=[select_user_by_token(command['token'])], data_type='users')

        if f == 'select_user_by_guid':
            return data_to_api_model(data=[select_user_by_guid(command['guid'])], data_type='users')

        if f == 'update_user':
            return data_to_api_model(data=update_user(api_model_to_data(users=command['users'])), data_type='Boolean')

        if f == 'insert_user':
            return data_to_api_model(data=insert_user(api_model_to_data(users=command['users'])), data_type='Boolean')

        if f == 'delete_user_by_guid':
            return data_to_api_model(data=delete_user_by_guid(command['guid']), data_type='Boolean')

        # Invite
        if f == 'insert_invite':
            return data_to_api_model(data=insert_invite(api_model_to_data(invites=command['invites'])), data_type='Boolean')

        if f == 'select_invite_by_key_guid':
            return data_to_api_model(data=[select_invite_by_key_guid(command['key_guid'])], data_type='invites')

        if f == 'select_invites_by_invite_guid':
            return data_to_api_model(data=select_invites_by_invite_guid(command['invite_guid']), data_type='invites')

        if f == 'select_invites_by_guid':
            return data_to_api_model(data=select_invites_by_guid(command['guid']), data_type='invites')

        if f == 'delete_invite_by_key_guid':
            return data_to_api_model(data=delete_invite_by_key_guid(command['key_guid']), data_type='Boolean')

        if f == 'delete_invites_by_guid':
            return data_to_api_model(data=delete_invites_by_guid(command['guid']), data_type='Boolean')

        if f == 'delete_invites_by_invite_guid':
            return data_to_api_model(data=delete_invites_by_invite_guid(command['invite_guid']), data_type='Boolean')

        # Friend
        if f == 'insert_friend':
            return data_to_api_model(data=insert_friend(api_model_to_data(friends=command['friends'])), data_type='Boolean')

        if f == 'select_friend_by_key_guid':
            return data_to_api_model(data=[select_friend_by_key_guid(command['key_guid'])], data_type='friends')

        if f == 'select_friends_by_guid':
            return data_to_api_model(data=select_friends_by_guid(command['guid']), data_type='friends')

        if f == 'update_friend_reply':
            return data_to_api_model(data=update_friend_reply(command['id'], command['friend_id'], command['reply']), data_type='Boolean')

        if f == 'delete_friend_by_key_guid':
            return data_to_api_model(data=delete_friend_by_key_guid(command['key_guid']), data_type='Boolean')

        if f == 'delete_friends_by_guid':
            return data_to_api_model(data=delete_friends_by_guid(command['guid']), data_type='Boolean')

        if f == 'delete_friends_by_friend_guid':
            return data_to_api_model(data=delete_friends_by_friend_guid(command['friend_guid']), data_type='Boolean')

        # Post
        if f == 'insert_post':
            return data_to_api_model(data=insert_post(api_model_to_data(posts=command['posts'])), data_type='Boolean')

        if f == 'select_posts_by_friends':
            friends = api_model_to_data(friends=command['friends'])
            if type(friends) != list:
                friends = [friends]
            return data_to_api_model(data=select_posts_by_friends(friends), data_type='posts')

        if f == 'delete_posts_by_guid':
            return data_to_api_model(data=delete_posts_by_guid(command['guid']), data_type='Boolean')

        # Join
        if f == 'select_join_by_guid_groupname':
            return data_to_api_model(data=[select_join_by_guid_groupname(command['guid'], command['groupname'])], data_type='joins')

        if f == 'select_joins_by_guid':
            return data_to_api_model(data=select_joins_by_guid(command['guid']), data_type='joins')

        if f == 'insert_join':
            return data_to_api_model(data=insert_join(api_model_to_data(joins=command['joins'])), data_type='Boolean')

        if f == 'delete_joins_by_guid':
            return data_to_api_model(data=delete_joins_by_guid(command['guid']), data_type='Boolean')

        # Group
        if f == 'select_group_by_groupname':
            return data_to_api_model(data=[select_group_by_groupname(command['groupname'])], data_type='groups')

        if f == 'select_all_groups':
            return data_to_api_model(data=select_all_groups(), data_type='groups')

        if f == 'insert_group':
            return data_to_api_model(data=insert_group(api_model_to_data(groups=command['groups'])), data_type='Boolean')

        # LastLogin
        if f == 'select_last_login_by_guid':
            return data_to_api_model(data=select_last_login_by_guid(command['guid']), data_type='str')

        if f == 'insert_last_login':
            return data_to_api_model(data=insert_last_login(command['guid'], command['last_login']), data_type='Boolean')

        if f == 'update_last_login':
            return data_to_api_model(data=update_last_login(command['guid'], command['last_login']), data_type='Boolean')

        if f == 'delete_last_login':
            return data_to_api_model(data=delete_last_login(command['guid']), data_type='Boolean')
