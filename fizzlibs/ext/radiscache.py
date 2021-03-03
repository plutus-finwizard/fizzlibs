import os
import redis

class RADIS_AUTHENTICATION_ERROR(Exception):
    pass

def __get_radis__():
    if not all([os.environ.get('REDIS_SERVICE_HOST'), os.environ.get('REDIS_SERVICE_PORT')]):
        raise RADIS_AUTHENTICATION_ERROR

    return redis.Redis(
            host=os.environ.get('REDIS_SERVICE_HOST'),
            port=os.environ.get('REDIS_SERVICE_PORT'),
            db=0
        )


def set(key, value, **kwargs):
    r = __get_radis__()
    r.set(key, value)

    if kwargs.get('time'):
        r.expire(key, **kwargs)


def get(key):
    return __get_radis__().get(key)


def delete(key):
    return __get_radis__().delete(key)



if __name__ == "__main__":
    import time

    set('name', 'buzz')
    print (f"{b'buzz'} == {get('name')}")
    print (f"{b'buzz'} == {get('name')}")

    delete('name')
    print (f"{'None'} == {get('name')}")

    set('amy', 'peterson', time=0)
    print (f"{b'perterson'} == {get('amy')}")

    set('pheobe', 'buffee', time=10)
    print ('Sleep (5)')

    time.sleep(5)
    print (f"{b'buffee'} == {get('pheobe')}")

    print ('Sleep (5)')
    time.sleep(5)
    print (f"{'None'} == {get('pheobe')}")
