import stomp
import json
import threading

listener_name = 'Listener'
queue_dir = '/queue/'
topic_dir = '/topic/'

ip = '3.84.189.214'
port = 61613

message_lock = threading.Lock()
group_message_counter = 0


class Listener(stomp.ConnectionListener):

    def on_message(self, headers, message):
        global message_lock, group_message_counter

        # Send the reply message to reply queue to response the server
        msg = json.loads(message)

        if 'status' in msg:
            message_lock.acquire(timeout=3)

            # Get the message of 'queue' format (send)
            if msg['status'] == 'q':
                id = msg['id']
                from_id = msg['from']
                print(msg['message'])
                send_to_reply_queue(id=id, from_id=from_id)

            # Get the message of 'topic' format (send-group)
            elif msg['status'] == 't':
                print(msg['message'])

                group_message_counter += 1

            else:
                print('[ERROR] Receive message wrong:', msg)

            message_lock.release()


def get_group_message_counter():
    global group_message_counter

    return int(group_message_counter)


def start_group_message_counter():
    global group_message_counter, message_lock

    message_lock.acquire(timeout=3)
    group_message_counter = 0
    message_lock.release()


def send_to_reply_queue(id=None, from_id=None):
    dst = queue_dir + id + '.reply.' + from_id

    send_data = {'status': 'r', 'id': id, 'from': from_id}

    try:
        conn = stomp.Connection12([(ip, port)])
        conn.start()
        conn.connect()
        conn.send(dst, json.dumps(send_data))
        conn.disconnect()
    except Exception as e:
        print('[ERROR] Client send to \'%s\' queue fail:' % id + '.reply.' + from_id, e)


def receive_message_from_mqserver(user_channel, group_channels):
    global message_lock

    conn = None

    dst = queue_dir + user_channel[0]

    try:
        conn = stomp.Connection12([(ip, port)])
        conn.set_listener(listener_name, Listener())
        conn.start()
        conn.connect()

        conn.subscribe(destination=dst, id=user_channel[1])

        if group_channels:
            try:
                for topic_name, topic_id in group_channels.items():
                    dst = topic_dir + topic_name

                    message_lock.acquire(timeout=3)
                    conn.subscribe(destination=dst, id=topic_id, ack='client-individual')
                    message_lock.release()

            except Exception as e:
                print('[ERROR] Client receive from topic fail:', e)

    except Exception as e:
        print('[ERROR] Client receive from server fail:', e)

    return conn


def unsubscribe_to_mqserver(conn, user_channels, group_channels):
    global message_lock

    if conn and conn.is_connected():
        conn.unsubscribe(id=user_channels[1])

        if group_channels:

            for topic_name, topic_id in group_channels.items():
                message_lock.acquire(timeout=3)

                try:
                    conn.unsubscribe(id=topic_id)

                except Exception as e:
                    pass
                    # print('[ERROR] Client unsubscribe to topic \'%s\', id = %s ,fail:' % (topic_name, topic_id), e)

                message_lock.release()

        conn.disconnect()
