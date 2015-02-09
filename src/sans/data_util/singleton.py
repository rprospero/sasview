'''
Singleton class to be used for objects that should only have one instance for
the life of each SasView session.

Created on Jan 20, 2015

@author: jkrzywon
'''

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]