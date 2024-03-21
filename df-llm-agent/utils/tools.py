import threading
import secrets
import time
import uuid

uuid_lock = threading.Lock()


def generate_uuid():
    """Generates uuid with date and mac
    """
    global uuid_lock
    with uuid_lock:
        new_uuid = uuid.uuid4()

    return str(new_uuid)


def generate_short_uuid():
    DIGITS = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '*', '-'
    ]

    def to_62_string(time_ms):
        mask = 62
        result = []
        while time_ms > 0:
            result.insert(0, DIGITS[int(time_ms % mask)])
            time_ms = int(time_ms / mask)
        return "".join(result)

    a = secrets.randbelow(62 * 62 * 62 - 1)
    time_str = to_62_string(int(time.time()))
    random_str = to_62_string(a)

    return time_str.zfill(7) + random_str.zfill(3)
