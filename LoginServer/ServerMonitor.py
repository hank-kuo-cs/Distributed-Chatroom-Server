import threading
import time
from CommandHandler import logout
from DatabaseBroker import *


class ServerMonitor(threading.Thread):
    def __init__(self, app_server_management, lock, timeout):
        threading.Thread.__init__(self)
        self.daemon = True
        self.app_server_management = app_server_management
        self.timeout = timeout
        self.lock = lock

    def _check_user_state(self, guid):
        last_login = send_sql_command(func='select_last_login_by_guid', keys=['guid'], datas=[guid])

        if not last_login or int(time.time()) - int(last_login) < self.timeout:
            return True

        return False

    def run(self):
        while True:
            time.sleep(self.timeout)

            self.lock.acquire()

            print('[Server Monitor] Check user idle situation')

            try:
                for app_server in self.app_server_management.app_servers:
                    for user_guid in app_server.users:
                        if not self._check_user_state(user_guid):
                            print('[Server Monitor] Wait user {} too long, logout it'.format(user_guid))
                            logout(['logout', user_guid], monitor_state=True)

            except Exception as e:
                print('[Server Monitor error] monitor fail:', e)

            self.lock.release()
