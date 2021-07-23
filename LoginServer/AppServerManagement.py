import socket
import threading
from EC2 import *


def check_app_server(server_ip):
    # Set up the socket to check the app server
    print('Start checking the app server...')

    t_start = time.time()
    while True:
        try:
            if time.time() - t_start > 60:
                break

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, 10008))
            s.close()

            print('Set up the app server {} success'.format(server_ip))
            return True

        except Exception as e:
            print(e, '\nApp server {} not set up yet, check again'.format(server_ip))
            time.sleep(5)

    print('[Check App Server Error] Timeout')
    return False


class AppServer:
    def __init__(self, id, ip):
        self.users = []
        self.id = id
        self.ip = ip

    def add_user(self, guid):
        if guid not in self.users:
            if self.isFull():
                print('[App Server Error] App server (id = {}, ip = {}) is full, cannot add more user'.format(self.id,
                                                                                                              self.ip))
            else:
                self.users.append(guid)
                return True

        return False

    def sub_user(self, guid):
        if self.isEmpty():
            print('[App Server Error] App server (id = {}, ip = {}) is empty, cannot sub more user'.format(self.id, self.ip))

        else:
            if guid in self.users:
                self.users.remove(guid)
                return True

        return False

    def isEmpty(self):
        if len(self.users) == 0:
            return True
        return False

    def isFull(self):
        if len(self.users) == 10:
            return True
        return False


class AppServerManageMent:
    def __init__(self):
        self.app_servers = []
        self.EC2 = EC2()
        self.thread_lock = threading.Lock()

    def _find_app_server(self, guid):
        res = -1
        isUserInAppServer = False

        try:
            if len(self.app_servers) != 0:
                for i, app_server in enumerate(self.app_servers):
                    if guid in app_server.users:
                        res = i
                        isUserInAppServer = True
                        break

                    if not app_server.isFull():
                        res = i
        except Exception as e:
            print('[AppManagement Error] Check app server fail:', e)

        return res, isUserInAppServer

    def _create_app_server(self, guid):
        try:
            app_server_id, app_server_ip = self.EC2.create_instance()

        except Exception as err:
            print('[App Management Error] Create app server fail:', err)
            return None

        if not app_server_id:
            print('[App Management Error] Id of the created server is None')
            return None

        app_server = AppServer(id=app_server_id, ip=app_server_ip)
        app_server.add_user(guid)

        self.app_servers.append(app_server)

        return app_server.ip

    def allocate_user_to_app_server(self, guid):
        self.thread_lock.acquire()

        app_server_index, isUserInAppServer = self._find_app_server(guid)

        if app_server_index == -1:
            app_server_ip = self._create_app_server(guid)
            if not check_app_server(app_server_ip):
                print('[AppManagement Error] Allocate user {} fail'.format(guid))
        else:
            app_server_ip = self.app_servers[app_server_index].ip
            if isUserInAppServer:
                print('[AppManagement] The user {} is already login'.format(guid))
            else:
                if not self.app_servers[app_server_index].add_user(guid):
                    print('[AppManagement Error] The user {} fail to add to app server {}'
                          .format(guid, self.app_servers[app_server_index].id))

        self.thread_lock.release()

        return app_server_ip

    def remove_user_from_app_server(self, guid):
        self.thread_lock.acquire()

        app_server_index, isUserInAppServer = self._find_app_server(guid)

        if not isUserInAppServer:
            print('[AppManagement Error] The user {} is not in any app server'.format(guid))

            self.thread_lock.release()
            return

        if not self.app_servers[app_server_index].sub_user(guid):
            print('[AppManagement Error] The user {} fail to sub from app server {}'
                  .format(guid, self.app_servers[app_server_index].id))

        if self.app_servers[app_server_index].isEmpty():
            if self.EC2.terminate_instance(self.app_servers[app_server_index].id):
                self.app_servers.pop(app_server_index)

        self.thread_lock.release()
