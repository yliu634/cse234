#!/usr/bin/env python

# This code is released under MIT license.

class Simon:
    def __init__(self, block_size, key_size, rounds, key_words, const_seq, key):
        self.word_size = block_size//2
        self.block_size = block_size
        self.key_size = key_size
        self.rounds = rounds
        self.key_words = key_words
        self.const_seq = const_seq
        self.mod = 1 << self.word_size
        self.expand_key = []
        tmp = '{:064x}'.format(key)
        for i in range(key_words):  # split keys, 64 bits for each key
            self.expand_key.append(int(tmp[-16:],16))
            tmp = tmp[:-16]
        self.key_expansion(key_words)
    
    # Reference: https://github.com/bozhu/NSA-ciphers
    def left_shift(self, x, i=1):
        return ((x << i) % self.mod) | (x >> (self.word_size - i))
    
    def right_shift(self, x, i=1):
        return ((x << (self.word_size - i)) % self.mod) | (x >> i)


    def key_expansion(self, key_words):
        c = (1 << self.word_size) - 4
        for i in range(key_words, self.rounds):
            k = self.right_shift(self.expand_key[-1], 3)
            if key_words == 4:
                k ^= self.expand_key[-3]
            k ^= self.right_shift(k,1) ^ self.expand_key[-key_words]
            k ^= c ^ self.const_seq[(i - key_words) % 62]
            self.expand_key.append(k)

    def encryption(self, plain):
        x = plain >> self.word_size
        y = plain % self.mod
        for i in range(self.rounds):
            tmp = x
            x = y ^ (self.left_shift(x, 1) & self.left_shift(x, 8)) ^ self.left_shift(x, 2) ^ self.expand_key[i]
            y = tmp
        return (x << self.word_size) | y

    def decryption(self, cipher):
        y = cipher >> self.word_size
        x = cipher % self.mod
        for i in range(self.rounds - 1, -1, -1):
            tmp = x
            x = y ^ (self.left_shift(x, 1) & self.left_shift(x, 8)) ^ self.left_shift(x, 2) ^ self.expand_key[i]
            y = tmp
        return (y << self.word_size) | x

    def encryption_simple(self, plain):
        x = plain >> self.word_size
        y = plain % self.mod   
        for i in range(self.rounds):
            tmp = x
            x = y ^ (self.left_shift(x, 1) ^ self.left_shift(x, 8)) ^ self.left_shift(x, 2) ^ self.expand_key[i]
            y = tmp
        return (x << self.word_size) | y
    
    def decryption_simple(self, cipher):
        y = cipher >> self.word_size
        x = cipher % self.mod
        for i in range(self.rounds - 1, -1, -1):
            tmp = x
            x = y ^ (self.left_shift(x, 1) ^ self.left_shift(x, 8)) ^ self.left_shift(x, 2) ^ self.expand_key[i]
            y = tmp
        return (y << self.word_size) | x


def enc(key, msg):
    cipher = SimonCipher(key)
    ct = b''
    l = len(msg)

    # Padding with 0's incase it isn't a multiple of the block size
    if len(msg) % 16 != 0:
        msg += (0).to_bytes(16 - (len(msg) % 16), byteorder="big", signed=False)

    for x in range(0, (len(msg) // 16)):
        blk = cipher.encrypt(x + 1)
        m = int.from_bytes(msg[(x * 16):(x * 16) + 16], byteorder="big", signed=False)
        ct += (m ^ blk).to_bytes(16, byteorder="big", signed=False)

    # Maybe check it should do the whole block and not just the length of the message.
    # TODO: Return a block or not
    return ct[0:l]



if __name__ == '__main__':
    # Configuration
    block_size = 128
    key_size = 256
    rounds = 72
    key_words = 4
    const_seq = [1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 
                 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 
                 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 
                 1, 1, 1, 0, 1, 1, 1, 1]    # z_4

    # Simon
    key = 0x1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100
    plaintext = 0x74206e69206d6f6f6d69732061207369
    # plaintext = 0x00f2ff4570a674f148c8cbbb5d57587a3a28c32d73be96829f9971341c718eefe1ccaf58c2d9c95c74e9a77f8716559d3e6e930092ec727f66748ddafc73225bff1e01fbee3c15b5314bc6ed869519438a33cebcac50533f892d9b476c17b52cead8d01b198db711d48469488964fe02d7975482218b8c1867930e18f9d8db4c6eb02bb648656c6c6f
    # ciphertext = 0x8d2b5579afc8a3a03bf72a87efe7b868
    my_simon = Simon(block_size, key_size, rounds, key_words, const_seq, key)
    cipher_out = my_simon.encryption(plaintext)
    plain_out = my_simon.decryption(cipher_out)
    print("Simon:")
    print("Test with key: 0x{:064x}".format(key))
    print("The input text for encryption is 0x{:032x}".format(plaintext))
    # print("The input text for decryption is 0x{:032x}".format(ciphertext))
    print("The encryption is 0x{:032x}".format(cipher_out))
    print("The decryption is 0x{:032x}".format(plain_out))


    # plaintext = 0x00f2ff4570a674f148c8cbbb5d57587a3a28c32d73be96829f9971341c718eefe1ccaf58c2d9c95c74e9a77f8716559d3e6e930092ec727f66748ddafc73225bff1e01fbee3c15b5314bc6ed869519438a33cebcac50533f892d9b476c17b52cead8d01b198db711d48469488964fe02d7975482218b8c1867930e18f9d8db4c6eb02bb648656c6c6f
    
    

    

 

    # # Simple Simon
    # key = 0x1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100
    # plaintext = 0x74206e69206d6f6f6d69732061207369
    # ciphertext = 0x4ce8fe4d694b9d8ebfb079f1cd198642
    # my_simon = Simon(block_size, key_size, rounds, key_words, const_seq, key)
    # cipher_out = my_simon.encryption_simple(plaintext)
    # plain_out = my_simon.decryption_simple(ciphertext)
    # print("Simple Simon:")
    # print("Test with key: 0x{:064x}".format(key))
    # print("The input text for encryption is 0x{:032x}".format(plaintext))
    # print("The input text for decryption is 0x{:032x}".format(ciphertext))
    # print("The encryption is 0x{:032x}".format(cipher_out))
    # print("The decryption is 0x{:032x}".format(plain_out))


    # test_key = 0x0
    # text_x = 0x2
    # text_y = 0x1
    # simonZ = Simon(block_size, key_size, rounds, key_words, const_seq, test_key)
    # out_y = simonZ.encryption_simple(text_x)

    # print("The encryption is 0x{:032x}".format(out_y))

    # out_y = simonZ.encryption_simple(1) ^ simonZ.encryption_simple(2)
    # print("The encryption is 0x{:032x}".format(out_y))

