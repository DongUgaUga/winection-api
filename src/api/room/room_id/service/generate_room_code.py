import random
import string

def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))