from logging import StreamHandler, basicConfig, DEBUG, getLogger, Formatter, INFO, WARNING, ERROR


def setup_logger(log_filename, level):
    level = get_log_level(level)
    format_str = '%(asctime)s@%(name)s %(levelname)s # %(message)s'
    basicConfig(filename=log_filename, level=level, format=format_str)
    stream_handler = StreamHandler()
    stream_handler.setFormatter(Formatter(format_str))
    getLogger().addHandler(stream_handler)


def get_log_level(level: str):
    level = level.lower()
    if level == 'debug':
        return DEBUG
    elif level == 'warning':
        return WARNING
    elif level == 'error':
        return ERROR
    else:
        return INFO
