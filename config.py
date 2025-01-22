import logging


class Config(object):
    def __str__(self):
        return self.__class__.__name__

    prefix = ','
    log_level = logging.INFO
    status = 'Chess'
    initial_extensions = [
        'cogs.admin',
        'cogs.chess'
    ]