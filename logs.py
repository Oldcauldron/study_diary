
import logging


def go_log():

    format_code = (u'%(filename)s[L:%(lineno)d]# %(levelname)-8s'
                   u'[%(asctime)s]%(message)s')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    form = logging.Formatter(format_code)
    handler = logging.FileHandler('study.log')
    # handler.setLevel(logging.DEBUG)
    handler.setFormatter(form)
    logger.addHandler(handler)

    return logger



