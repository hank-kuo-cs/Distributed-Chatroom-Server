import json
import stomp
from DB_Broker import send_sql_command

listener_name = 'Listener'
queue_dir = '/queue/'
topic_dir = '/topic/'

ip = '3.84.189.214'
port = 61613


class Listener(stomp.ConnectionListener):

    def on_message(self, headers, message):
        response = json.loads(message)

        if 'status' in response:
            if response['status'] == 'r':
                if not send_sql_command(func='update_friend_reply',
                                        keys=['id', 'friend_id', 'reply'],
                                        datas=[response['id'], response['from'], 1]):
                    print({'status': 1, 'message': 'SQL Error'})


def send_to_queue(msg=None, id=None, friend_id=None):
    try:
        queue_name = queue_dir + friend_id

        send_data = {'status': 'q', 'id': friend_id, 'message': msg, 'from': id}

        conn = stomp.Connection12([(ip, port)])
        conn.start()
        conn.connect()
        conn.send(queue_name, json.dumps(send_data))
        conn.disconnect()

    except Exception as e:
        print('[ERROR] Server send to the \'%s\' queue fail:' % friend_id, e)


def send_to_topic(msg=None, id=None, group_name=None):
    try:
        topic_name = topic_dir + group_name

        send_data = {'status': 't', 'group': group_name, 'message': msg, 'from': id}

        conn = stomp.Connection12([(ip, port)])
        conn.start()
        conn.connect()
        conn.send(topic_name, json.dumps(send_data))
        conn.disconnect()

    except Exception as e:
        print('[ERROR] Server send to the \'%s\' topic fail:' % group_name, e)


def receive_from_queue(id=None, friend_id=None, channel_id=None):
    conn = None

    try:
        if id:
            queue_name = queue_dir + friend_id + '.reply.' + id
        else:
            queue_name = queue_dir + friend_id

        conn = stomp.Connection12([(ip, port)])
        conn.set_listener(listener_name, Listener())
        conn.start()
        conn.connect()
        conn.subscribe(destination=queue_name, id=channel_id)

    except Exception as e:
        print('[ERROR] Server receive from the \'%s\' queue fail:' % friend_id + '.reply.' + id, e)

    return conn


def unsubscribe_from_queue(conn, queue_name, channel_id):
    try:
        if conn:
            conn.unsubscribe(id=channel_id)
            conn.disconnect()

    except Exception as e:
        print('[ERROR] Server unsubscribe from %s fail:' % queue_name, e)
