from hashlib import sha256


def create_digest(data, func=None):
    func = func or sha256
    obj = func()
    obj.update(data)
    return obj.hexdigest()
