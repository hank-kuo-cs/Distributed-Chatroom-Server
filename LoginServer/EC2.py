import boto3
import time

user_data = '''#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-stomp
git clone https://github.com/yuliangkuocs/Distribute_Server.git
python3 Distribute_Server/AppServer.py 0.0.0.0 10008
'''


class EC2:
    def __init__(self):
        self.ec2_resource = boto3.resource(service_name='ec2',
                                           region_name='us-east-1',
                                           aws_access_key_id='',
                                           aws_secret_access_key='')
        self.main_instance_id = 'i-0b43587548c5abc49'
        self.image_id = 'ami-0ac019f4fcb7cb7e6'
        self.security_group_id = 'sg-02f32258cb75a2d64'
        self.key = 'key'
        self.instance_type = 't2.micro'
        self.instance_ids = self._get_instance_ids()
        self.user_data = user_data

    def _get_instance_ids(self):
        return [instance.id for instance in self.ec2_resource.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': [
                        'running', 'pending'
                    ]
                },
            ]
        )]

    def _get_instance_id_and_ip(self, instance_id):
        t_start = time.time()

        while True:
            print('[EC2] Check instance {} whether running'.format(instance_id))
            if time.time() - t_start > 90:
                return None, None

            instances = self.ec2_resource.instances.filter(Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': [
                        'running'
                    ]
                },
            ])

            instance = [i for i in instances if i.id == instance_id]
            instance = instance[0] if instance else None

            if not instance:
                time.sleep(5)
            else:
                break

        print('instance (id = {}, ip = {}) is running'.format(instance.id, instance.public_ip_address))
        return instance.id, instance.public_ip_address

    def create_instance(self):
        self.ec2_resource.create_instances(
            ImageId=self.image_id,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[self.security_group_id],
            InstanceType=self.instance_type,
            KeyName=self.key,
            UserData=self.user_data
        )
        print('[EC2] Create instance success')

        new_instance_ids = self._get_instance_ids()
        new_instance_id = [instance_id for instance_id in new_instance_ids if instance_id not in self.instance_ids]
        new_instance_id = new_instance_id[0] if new_instance_id else None

        if new_instance_id:
            self.instance_ids.append(new_instance_id)
        else:
            print('[EC2 Error] There is no new instance id created')
            return

        return self._get_instance_id_and_ip(new_instance_id)

    def terminate_instance(self, instance_id):
        print('[EC2] Terminate instance {}'.format(instance_id))

        if instance_id == self.main_instance_id:
            print('[EC2 Error] You Cannot terminate your main instance')
            return False

        instances = self.ec2_resource.instances.filter(
            InstanceIds=[
                instance_id,
            ],
        )

        for instance in instances:
            instance.terminate()

            try:
                self.instance_ids.remove(instance_id)
            except Exception as err:
                print('[ERROR] Remove instance id {0} fail:'.format(instance_id), err)
                return False

        return True
