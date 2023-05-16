import os
import logging
import datetime
from typing import Optional, Literal
import pytz


class Formatter(logging.Formatter):
    '''override logging.Formatter to use an aware datetime object.
    '''
    def __init__(self,
                 fmt=None,
                 datefmt=None,
                 style='%',
                 timezone='Asia/Bangkok'):
        logging.Formatter.__init__(self,
                                   fmt=fmt,
                                   datefmt=datefmt,
                                   style=style)
        self.timezone = timezone

    def converter(self,
                  timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp,
                                             tz=pytz.timezone('utc'))
        tzinfo = pytz.timezone(self.timezone)
        dt = dt.astimezone(tzinfo)
        return dt

    def formatTime(self,
                   record,
                   datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s


class LogCollector():
    '''LogCollector

    :param logger_name: Logger Name
    :type logger_name: str

    :param environment: Running environment.
    :type environment: Literal['DEV', 'NON_PROD', 'PROD'], optional, defaults to  'DEV'

    :param time_zone: Time zone to be shown in the log, check possible value in pytz.all_timezones.
    :type time_zone: str, optional, defaults to 'Asia/Bangkok'

    :param print_log: Print log on screen.
    :type print_log: bool, optional, defaults to True

    :param write_log: Write log to file.
    :type write_log: bool, optional, defaults to False

    :param log_dir: Directory to write log file.
    :type log_dir: str, optional, defaults to  'log/'

    :param log_file_name: Log file name.
    :type log_file_name: str, optional, defaults to  'log'

    :param add_log_file_name_dt_prefix: Add log file name prefix.
    :type add_log_file_name_dt_prefix: bool, optional, defaults to True

    :param dt_prefix_format: Prefix date time format for log file.
                             Check the format syntax in: https://strftime.org/
    :type dt_prefix_format: str, optional, defaults to '%Y%m%d%H'

    '''

    def __init__(self,
                 logger_name: str,
                 environment: Optional[Literal['DEV', 'NON_PROD', 'PROD']] = 'DEV',
                 time_zone: Optional[str] = 'Asia/Bangkok',
                 print_log: Optional[bool] = True,
                 write_log: Optional[bool] = False,
                 log_dir: Optional[str] = 'log/',
                 log_file_name: Optional[str] = 'log',
                 add_log_file_name_dt_prefix: Optional[bool] = True,
                 dt_prefix_format: Optional[str] = '%Y%m%d%H'):

        self.__default_dir = os.path.dirname(os.path.realpath(__file__)).rsplit(os.path.sep, 1)[0]
        self.__dir = os.path.join(self.__default_dir, *f'{log_dir}'.split('/'))

        if add_log_file_name_dt_prefix:
            self.__date_now = datetime.datetime.now(pytz.timezone(time_zone)).strftime(dt_prefix_format)
            self.__path = os.path.join(self.__dir, f'{str(self.__date_now)}_{log_file_name}')
        else:
            self.__path = os.path.join(self.__dir, f'{log_file_name}')

        self.__logger_name = logger_name
        self.__log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

        # DEBUG > INFO > WARNING > ERROR > CRITICAL

        if environment == 'DEV':
            self.__log_level_print = logging.DEBUG
            self.__log_level_file = logging.DEBUG
        elif environment == 'NON_PROD':
            self.__log_level_print = logging.INFO
            self.__log_level_file = logging.ERROR
        elif environment == 'PROD':
            self.__log_level_print = logging.INFO
            self.__log_level_file = logging.ERROR
        else:
            self.__log_level_print = logging.DEBUG
            self.__log_level_file = logging.DEBUG

        handler_format = Formatter(self.__log_format, timezone=time_zone)

        # Create logger
        self.logger = logging.getLogger(self.__logger_name)
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG)

        if print_log:
            # Create handlers
            print_handler = logging.StreamHandler()
            # Set Level of handlers
            print_handler.setLevel(self.__log_level_print)
            # Create formatters
            print_handler.setFormatter(handler_format)
            # Add handlers to the logger
            self.logger.addHandler(print_handler)

        if write_log:
            os.makedirs(self.__dir, exist_ok=True, mode=777)
            # Create handlers
            file_handler = logging.FileHandler(self.__path)
            # Set Level of handlers
            file_handler.setLevel(self.__log_level_file)
            # Create formatters
            file_handler.setFormatter(handler_format)
            # Add handlers to the logger
            self.logger.addHandler(file_handler)

    def collect(self,
                level: str,
                message: object):
        '''
        Call the collect method everywhere you want to track back and keep in "log" directory,
        the name of files depend on date in format 'yyyy-mm-dd'.

        ps.
        In development, logs will be printed and keep when the logs are greater or equal to the WARNING level.
        In production, logs will be only kept if the logs are greater than or equal to the ERROR level.

        :param level: Level of log
                      Possible value ordered by the impact of criticalness increasing:
                      "DEBUG", "INFO", "WARNING", "ERROR", and "CRITICAL"
        :type level: str

        :param message: Log message
        :type message: str

        '''
        level_dict = {'debug': self.logger.debug,
                      'info': self.logger.info,
                      'warning': self.logger.warning,
                      'error': self.logger.error,
                      'critical': self.logger.critical}

        level = level.lower()
        printer = level_dict.get(level, self.logger.debug)

        if isinstance(message, str):
            printer(message)
        else:
            obj_str = message.__str__()
            message = '\n' + obj_str
            printer(message)


if __name__ == '__main__':

    # Example of using
    log_obj = LogCollector(logger_name=__file__.split(os.path.sep)[-1],
                           environment='DEV',
                           time_zone='Asia/Bangkok',
                           print_log=False,
                           write_log=True,
                           log_dir='log/',
                           log_file_name='test')
    d = {2, 3, 4, 4}
    data = f'test_data{d}'
    log_obj.collect('DEBUG', data)
    log_obj.collect('INFO', data)
    log_obj.collect('WARNING', data)
    log_obj.collect('ERROR', data)
    log_obj.collect('CRITICAL', data)
