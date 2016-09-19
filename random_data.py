import random, string
from random import randint

# Gets random data to use in samples
class RandomData:
    # Gets random characters to use for generating unique name.
    def get_random_name(self, length):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    # Gets Random Bytes of specified size for use in samples.
    # Input Arguments:
    # size - size of random bytes to get
    def get_random_bytes(self, size):
        rand = random.Random()
        result = bytearray(size)
        for i in range(size):
            result[i] = rand.randint(0, 255)
        return bytes(result)