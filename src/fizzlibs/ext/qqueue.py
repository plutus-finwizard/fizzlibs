import os
import pickle
import logging
import base64
import mock
import google.auth
import google.api_core
from google.cloud import pubsub_v1
from google.api_core import retry


class QQUEUE_INVALID_PROJECT_ID(Exception):
    pass

class QQUEUE_AUTHENTICATION_ERROR(Exception):
    pass


class Task(object):
    """
    A class to represent a `Cloud Task`

    ...

    Attributes
    ----------
    """
    def __init__(self, payload, method='PUSH', tag=None, countdown=None):
        """
        Parameters
        ----------
        payload : str
            Message of the task
        method : str
            Determines if messages should be pushed to subscriber
            or subscriber should pull (default is PUSH)
        tag : str
            Publisher can group messages by tag, which can be used by
            subscriber to retrieve it.

            Note: This is not applicable if method type is PUSH
        countdown : int

            Note: Implementation pending 
        """

        self.payload = payload
        self.method = method or 'PUSH'
        self.tag = tag if self.method == 'PULL' else None
        self.countdown = countdown

    def to_pickle(self):
        '''
        TODO: Add encryption algorithm for added security
        '''
        return base64.b64encode(
            pickle.dumps(self, protocol=2, fix_imports=True)
        )

    def from_pickle(self, data):
        '''
        TODO: Add decryption algorithm for added security
        '''
        return pickle.loads(base64.b64decode(data), fix_imports=True)

    def __repr__(self):
        return f'{self.__class__.__name__} : {self.payload}, {self.method}'


class QQueue(object):
    """
    A class to add or lease message to-and-from queue 

    ...

    Attributes
    ----------
    """
    def __init__(self, name, **kwargs):
        self.project_id = os.environ.get('QQUEUE_PROJECT_ID')

        if os.environ.get('GKE_SOFTWARE_ID'):
            self.queue_name = f'{os.environ.get("GKE_SOFTWARE_ID")}-{self.name}'
        else:
            self.queue_name = name

        if not self.project_id:
            raise QQUEUE_INVALID_PROJECT_ID

        if kwargs.pop('initialize_queue'):
            # Create queue
            self.__create_queue()
            # Create enduser
            if kwargs.pop('mode') == 'pull':
                self.__create_enduser()

    def __get_credentials(self):
        if os.environ.get('PUBSUB_EMULATOR_HOST'):
            # As pubsub_v1 looks for this env variable,
            # We will also use the same to create mock credentials
            return mock.Mock(spec=google.auth.credentials.Credentials)

        if self.project_id == os.environ.get('QQUEUE_PROJECT_ID') and os.environ.get('QQUEUE_SERVICE_KEY'):
            # Getting default qqueue service account
            return google.auth.credentials.Credentials.from_service_account_file(
                    os.environ.get('QQUEUE_SERVICE_KEY'),
                    scopes=SCOPES
                )

        raise QQUEUE_AUTHENTICATION_ERROR

    def __get_subscriber(self):
        return pubsub_v1.SubscriberClient(credentials=self.__get_credentials())

    def __get_publisher(self):
        return pubsub_v1.PublisherClient(credentials=self.__get_credentials())

    def __create_queue(self):
        """ Creates a pubsub topic
        """
        publisher = self.__get_publisher()
        topic_path = publisher.topic_path(self.project_id, self.queue_name)

        # Check if topic exists
        if publisher.get_topic(topic=topic_path):
            logging.info(f'Queue {topic_path} exists. Skipping creation')
            return

        topic = publisher.create_topic(request={'name': topic_path})

        logging.info('Created queue: {topic.name}')

    def __create_enduser(self):
        """ Creates a pubsub subscriber for a given topic
        """
        publisher = self.__get_publisher()
        subscriber = self.__get_subscriber()

        topic_path = publisher.topic_path(self.project_id, self.queue_name)
        subscription_path = subscriber.subscription_path(self.project_id, self.queue_name)

        if subscriber.get_subscription(subscription=subscription_path):
            logging.info (f'End user for {subscription_path} exists')
            return

        with subscriber:
            subscription = subscriber.create_subscription(
                request={'name': subscription_path, 'topic': topic_path}
            )

        logging.info(f'Queue default enduser: {subscription}')

    def lease_tasks_by_tag(self, lease_seconds=600, max_tasks=100):
        pass

    def lease_tasks(self, lease_seconds=600, max_tasks=100):
        subscriber = self.__get_subscriber()
        subscription_path = subscriber.subscription_path(self.project_id, self.queue_name)

        with subscriber:
            response = subscriber.pull(
                subscription=subscription_path,
                max_messages=max_tasks,
                retry=retry.Retry(deadline=300)
            )

            ack_ids = [received_message.ack_id for received_message in response.received_messages]

            subscriber.modify_ack_deadline(
                request={
                    "subscription": subscription_path,
                    "ack_ids": ack_ids,
                    # Must be between 10 and 600.
                    "ack_deadline_seconds": 15
                }
            )

            # subscriber.acknowledge(subscription=subscription_path, ack_ids=ack_ids)

            print(
                f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}."
            )

        return response.received_messages

    def add(self, data):
        publisher = self.__get_publisher()
        topic_path = publisher.topic_path(self.project_id, self.queue_name)

        future = publisher.publish(
            topic_path, data #, origin="python-sample", username="gcp"
        )

        print(future.result())

    def add_async(self):
        pass

    def modify_task_lease(self):
        pass

    def delete_tasks(self):
        pass

    def delete_tasks_async(self):
        pass

    def purge(self):
        pass

    def fetch_statistics(self, deadline=None):
        pass

    # def seek(self):
    #     subscriber = self.__get_subscriber()
    #     subscription_path = subscriber.subscription_path(self.project_id, self.queue_name)

    #     with subscriber:
    #         subscriber.seek(
    #                 subscription=subscription_path,
    #                 max_messages=3,
    #                 retry=retry.Retry(deadline=300)
    #             )

    # def add(self, data):
    #     publisher = self.__get_publisher()
    #     topic_path = publisher.topic_path(self.project_id, self.queue_name)

    #     future = publisher.publish(
    #         topic_path, data #, origin="python-sample", username="gcp"
    #     )

    #     print(future.result())


if __name__ == "__main__":
    import _thread
    import time

    # Test Task
    aTask = Task("I'm a task", method="PULL", tag="I'm unique", countdown=1)
    print(aTask)
    print(aTask.to_pickle())
    print(aTask.from_pickle(aTask.to_pickle()))

    # # Test QQueue
    # try:
    #     aQueue = QQueue('imqueue')
    #     aQueue.create_topic()
    # except google.api_core.exceptions.AlreadyExists as e:
    #     # Ignoring existing topic here, testing purpose
    #     pass

    # # Publish message
    # for n in range(1, 10):
    #     data = "Message number {}".format(n)
    #     # Data must be a bytestring
    #     data = data.encode("utf-8")
    #     # Add two attributes, origin and username, to the message
    #     QQueue('imqueue').add(data)

    # # Create subscription
    # try:
    #     bQueue = QQueue('imqueue')
    #     bQueue.create_subscription()
    # except google.api_core.exceptions.AlreadyExists as e:
    #     # Ignoring existing subscription here, testing purpose
    #     pass

    # # Pull messages
    # cQueue = QQueue('imqueue')
    # print (cQueue.lease_tasks())

    def print_time( threadName, delay):
        print (f'{threadName} -------------------------------')
        # count = 0
        # while count < 5:
        #     time.sleep(delay)
        #     count += 1
        #     print(f"{threadName}: {time.ctime(time.time())}")
        cQueue = QQueue('imqueue')
        print (cQueue.lease_tasks())

    # Create two threads as follows
    try:
        _thread.start_new_thread( print_time, ("Thread-1", 2) )
        _thread.start_new_thread( print_time, ("Thread-2", 2) )
    except Exception as e:
        print(str(e))

    while 1:
        pass
