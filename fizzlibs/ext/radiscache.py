import os
import json
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


def __sanitize_key__(key):
    suffix = os.environ.get('GKE_SOFTWARE_ID')

    if suffix:
        return f'{suffix}-key'

    return key


def set(key, value, **kwargs):
    key = __sanitize_key__(key)
    value = json.dumps(value) if value else value

    r = __get_radis__()
    r.set(key, value)

    if kwargs.get('time'):
        r.expire(key, **kwargs)


def get(key):
    key = __sanitize_key__(key)
    value = __get_radis__().get(key)

    if value:
        return json.loads(value)

    return value


def delete(key):
    key = __sanitize_key__(key)
    return __get_radis__().delete(key)



if __name__ == "__main__":
    import time

    set('c', 'buzz')
    print (f"{b'buzz'} == {get('c')}")
    print (f"{b'buzz'} == {get('c')}")

    delete('c')
    print (f"{'None'} == {get('c')}")

    set('amy', 'peterson', time=0)
    print (f"{b'perterson'} == {get('amy')}")

    set('pheobe', 'buffee', time=10)
    print ('Sleep (5)')

    time.sleep(5)
    print (f"{b'buffee'} == {get('pheobe')}")

    print ('Sleep (5)')
    time.sleep(5)
    print (f"{'None'} == {get('pheobe')}")

    set('k', {'x': 'hello'})
    set('k', 1)
