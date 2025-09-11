import os
import sys
import time

try:
    if sys.platform != 'win32':
        os.environ['TZ'] = 'Asia/Shanghai'
        time.tzset()
except Exception as e:
    print(f'时区设置失败,请手动设置后重试,原因"{e}"')

import logging
import urllib3
from rich.console import Console
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

urllib3.disable_warnings()
LOG_TIME_FORMAT = '[%Y-%m-%d %H:%M:%S]'
console = Console(log_path=False, log_time_format=LOG_TIME_FORMAT)
__version__ = '1.0.0'
__license__ = 'MIT License'
__update_date__ = '2025/09/09 15:43:33'
__copyright__ = f'Copyright (C) 2024-{__update_date__[:4]}'
SOFTWARE_FULL_NAME = 'NZ_Helper_Sign'
SOFTWARE_SHORT_NAME = 'NHS'
APPDATA_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
os.makedirs(APPDATA_PATH, exist_ok=True)
LOG_PATH = os.path.join(APPDATA_PATH, f'{SOFTWARE_SHORT_NAME}_LOG.log')
MAX_LOG_SIZE = 200 * 1024 * 1024
BACKUP_COUNT = 0
LOG_FORMAT = '%(name)s:%(funcName)s:%(lineno)d - %(message)s'
FILE_LOG_LEVEL: int = logging.INFO
CONSOLE_LOG_LEVEL: int = logging.WARNING
file_handler = RotatingFileHandler(
    filename=LOG_PATH,
    maxBytes=MAX_LOG_SIZE,
    backupCount=BACKUP_COUNT,
    encoding='UTF-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s' + ' ' + LOG_FORMAT, datefmt=LOG_TIME_FORMAT))
file_handler.setLevel(logging.getLevelName(FILE_LOG_LEVEL))
console_handler = RichHandler(
    level=CONSOLE_LOG_LEVEL,
    console=console,
    rich_tracebacks=True,
    show_path=False,
    omit_repeated_times=False,
    log_time_format=LOG_TIME_FORMAT
)
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt=LOG_TIME_FORMAT,
    handlers=[
        console_handler,
        file_handler
    ]
)
log = logging.getLogger('rich')
