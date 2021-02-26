import os
import pickle
import logging
import base64
import mock
import google.auth
import google.api_core
from google.api_core import retry
from google.cloud.pubsub import types
from google.cloud import pubsub_v1


class QQUEUE_INVALID_PROJECT_ID(Exception):
    pass

class QQUEUE_AUTHENTICATION_ERROR(Exception):
    pass

class QQUEUE_EMPTY_TASKS_ERROR(Exception):
    pass

class QQUEUE_TASK_TYPE_ERROR(Exception):
    pass

class QQUEUE_TASKS_MAX_LIMIT_ERROR(Exception):
    pass

QQUEUE_MAX_TASKS_LIMIT = 1000
QQUEUE_MAX_BATCH_LIMIT = 500

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

    @classmethod
    def from_pickle(cls, data):
        '''
        TODO: Add decryption algorithm for added security
        '''
        return pickle.loads(base64.b64decode(data), fix_imports=True)

    @classmethod
    def from_grpc_response(cls, grpc_response):
        task = cls.from_pickle(grpc_response.message.data)
        task.ack_id = grpc_response.ack_id

        return task

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

        if kwargs.get('initialize_queue', False):
            # Create queue
            self.__create_queue()
            # Create enduser
            if kwargs.get('mode') == 'pull':
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
        subscriber = pubsub_v1.SubscriberClient(credentials=self.__get_credentials())

        return (
            subscriber,
            subscriber.subscription_path(self.project_id, self.queue_name)
        )

    def __get_publisher(self):
        publisher = pubsub_v1.PublisherClient(
                credentials=self.__get_credentials(),
                batch_settings=types.BatchSettings(max_messages=QQUEUE_MAX_BATCH_LIMIT)
            )

        return (
            publisher,
            publisher.topic_path(self.project_id, self.queue_name)
        )

    def __create_queue(self):
        """ Creates a pubsub topic
        """
        publisher, source = self.__get_publisher()

        # Check if topic exists
        try:
            publisher.get_topic(topic=source)
            logging.info(f'Queue {source} exists. Skipping creation')
            return
        except google.api_core.exceptions.NotFound:
            pass

        topic = publisher.create_topic(request={'name': source})

        logging.info('Created queue: {topic.name}')

    def __create_enduser(self):
        """ Creates a pubsub subscriber for a given topic
        """
        publisher, p_source = self.__get_publisher()
        subscriber, s_source = self.__get_subscriber()

        try:
            subscriber.get_subscription(subscription=s_source)
            logging.info (f'End user for {s_source} exists')
            return
        except google.api_core.exceptions.NotFound:
            pass

        with subscriber:
            subscription = subscriber.create_subscription(
                request={'name': s_source, 'topic': p_source}
            )

        logging.info(f'Queue default enduser: {subscription}')

    def __sanitize_tasks(self, tasks):
        if not tasks:
            raise QQUEUE_EMPTY_TASKS_ERROR

        if isinstance(tasks, list):
            if len(tasks) > QQUEUE_MAX_TASKS_LIMIT:
                raise QQUEUE_TASKS_MAX_LIMIT_ERROR

            if type(tasks[0]) is not Task:
                raise QQUEUE_TASK_TYPE_ERROR
        elif type(tasks) is not Task:
            raise QQUEUE_TASK_TYPE_ERROR

    def lease_tasks_by_tag(self, lease_seconds=600, max_tasks=100):
        pass

    def lease_tasks(self, lease_seconds=600, max_tasks=100):
        subscriber, source = self.__get_subscriber()

        with subscriber:
            response = subscriber.pull(
                subscription=source,
                max_messages=max_tasks,
                return_immediately=True,
                retry=retry.Retry(deadline=300)
            )

            if not response.received_messages:
                return []

            ack_ids = [received_message.ack_id for received_message in response.received_messages]

            subscriber.modify_ack_deadline(
                request={
                    "subscription": source,
                    "ack_ids": ack_ids,
                    # Must be between 10 and 600.
                    "ack_deadline_seconds": lease_seconds
                }
            )

        return list(map(
            lambda x: Task.from_grpc_response(x), response.received_messages
        ))

    def add(self, tasks):
        futures = self.add_async(tasks)

        if isinstance(futures, list):
            return [x.result() for x in futures]

        return futures.result()

    def add_async(self, tasks):
        """Add task(s) to queue
        ...
        Parameter
        ---------
        tasks : Task or list of Task

        Returns
        -------
        A future object of a list of future objects
        which results to message id
        """
        self.__sanitize_tasks(tasks)

        publisher, source = self.__get_publisher()

        futures = []

        if isinstance(tasks, list):
            for tasks in tasks:
                future = publisher.publish(
                    source, tasks.to_pickle()
                )
                futures.append(future)

        else:
            futures = publisher.publish(
                source, tasks.to_pickle()
            )

        return futures

    def modify_task_lease(self, tasks, lease_seconds=600):
        self.__sanitize_tasks(tasks)
        tasks = tasks if isinstance(tasks, list) else [tasks]
        ack_ids = [task.ack_id for task in tasks]

        subscriber, source = self.__get_subscriber()
        subscriber.modify_ack_deadline(
            request={
                "subscription": source,
                "ack_ids": ack_ids,
                # Must be between 10 and 600.
                "ack_deadline_seconds": lease_seconds
            }
        )

    def delete_tasks(self, tasks):
        self.__sanitize_tasks(tasks)
        subscriber, source = self.__get_subscriber()

        tasks = tasks if isinstance(tasks, list) else [tasks]
        ack_ids = [task.ack_id for task in tasks]

        subscriber.acknowledge(subscription=source, ack_ids=ack_ids)

    def delete_tasks_async(self):
        pass

    def purge(self):
        pass

    def fetch_statistics(self, deadline=None):
        pass










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

    # Pull messages
    cQueue = QQueue('default')
    print (cQueue.lease_tasks())

    # def print_time( threadName, delay):
    #     print (f'{threadName} -------------------------------')
    #     # count = 0
    #     # while count < 5:
    #     #     time.sleep(delay)
    #     #     count += 1
    #     #     print(f"{threadName}: {time.ctime(time.time())}")
    #     cQueue = QQueue('imqueue')
    #     print (cQueue.lease_tasks())

    # # Create two threads as follows
    # try:
    #     _thread.start_new_thread( print_time, ("Thread-1", 2) )
    #     _thread.start_new_thread( print_time, ("Thread-2", 2) )
    # except Exception as e:
    #     print(str(e))

    # while 1:
    #     pass
