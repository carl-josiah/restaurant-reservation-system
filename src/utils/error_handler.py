import sys
import datetime
from src.utils.constants import CAT_ERROR, CAT_SUCCESS


def _log_to_file(message, category):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] [{category}] {message}"
    with open("system_audit.log", "a") as f:
        f.write(log_entry + "\n")
    return log_entry


def show_message(message, category=CAT_SUCCESS):
    log_entry = _log_to_file(message, category)
    sys.stdout.write(f" {log_entry}\n")


def log_error(message, category=CAT_ERROR):
    log_entry = _log_to_file(message, category)
    sys.stderr.write(f" {log_entry}\n")
