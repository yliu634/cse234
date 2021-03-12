import numpy as np
import binascii

#Iota Step Round Constants For Keccak-p(1600, 24)
IOTA_CONSTANTS = np.array([0x0000000000000001,0x0000000000008082, 0x800000000000808A,
                            0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
                            0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
                            0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
                            0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
                            0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
                            0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
                            0x8000000000008080, 0x0000000080000001, 0x8000000080008008],
                          dtype=np.uint64)

#Lane Shifts for Rho Step
RHO_SHIFTS = np.array([[0, 36, 3, 41, 18],
                       [1, 44, 10, 45, 2],
                       [62, 6, 43, 15, 61],
                       [28, 55, 25, 21, 56],
                       [27, 20, 39, 8, 14]], dtype=np.uint64)


#Row Re-order Mapping for Pi Step
PI_ROW_REORDER = np.array([[0, 3, 1, 4, 2],
                           [1, 4, 2, 0, 3],
                           [2, 0, 3, 1, 4],
                           [3, 1, 4, 2, 0],
                           [4, 2, 0, 3, 1]])

#Column Re-order Mapping for Pi Step
PI_COLUMN_REORDER = np.array([[0, 0, 0, 0, 0],
                              [1, 1, 1, 1, 1],
                              [2, 2, 2, 2, 2],
                              [3, 3, 3, 3, 3],
                              [4, 4, 4, 4, 4]])

def cir_shift_array(a,n):
    return a[n:] + a[:n]

def cir_shift_bit64(a,n,left = 1):
    if left==1:
        return a << n | a >> 64-n
    else:
        return a >> n | a << 64-n

def f_function(state):
    state = np.copy(np.frombuffer(state, dtype=np.uint64, count=25).reshape([5, 5], order='F'))
    for round_num in range(24):
        # theta_step:
        shift_z = cir_shift_bit64(state,1)
        state ^= np.bitwise_xor.reduce(state[cir_shift_array(list(range(5)),-1) ], axis = 1, keepdims=True) ^ np.bitwise_xor.reduce(shift_z[cir_shift_array(list(range(5)),1) ],  axis = 1, keepdims=True)
     
        # rho_step:
        state = cir_shift_bit64(state,RHO_SHIFTS)

        # pi_step:
        # based on pre-calculated positions
        state = state[PI_ROW_REORDER, PI_COLUMN_REORDER]

        # chi_step:
        state ^= ~state[cir_shift_array(list(range(5)),1) ] & state[cir_shift_array(list(range(5)),2) ]

        # iota_step:
        # based on pre-calculated constants
        state[0, 0] ^= IOTA_CONSTANTS[round_num]
    
    return bytearray(state.tobytes(order='F'))


def SHA3_512(inputBytes):
    rate = 576
    capacity = 1024
    outputByteLen = 512//8
    state = bytearray([0]*200)
    rateInBytes = rate//8
    blockSize = 0
    inputOffset = 0
    # absorbing
    while(inputOffset < len(inputBytes)):
        blockSize = min(len(inputBytes)-inputOffset, rateInBytes)
        for i in range(blockSize):
            state[i] = state[i] ^ inputBytes[i+inputOffset]
        inputOffset = inputOffset + blockSize
        if (blockSize == rateInBytes):
            state = f_function(state)
            blockSize = 0
    # padding
    state[blockSize] = state[blockSize] ^ 0x06
    state[rateInBytes-1] = state[rateInBytes-1] ^ 0x80
    state = f_function(state)
    # squeezing
    outputBytes = bytearray()
    while(outputByteLen > 0):
        blockSize = min(outputByteLen, rateInBytes)
        outputBytes = outputBytes + state[0:blockSize]
        outputByteLen = outputByteLen - blockSize
        if (outputByteLen > 0):
            state = f_function(state)
    return outputBytes


if __name__ == "__main__":
    
    out = SHA3_512(bytearray(binascii.unhexlify('0000')))

    msg = b'Hello'

    # a = bytes(msg)
    # print(a)

    out = SHA3_512(out)

    print("The hashed output:")
    print(binascii.hexlify(out))
    # reference = bytearray(binascii.unhexlify('71cb4a0b4d323a3d9d6f8188db4d3266a298053c660a5152afebd0782d07820d7af7e4b1f327e150753fd5cc84b3cf949f33f7a64d62cd764c154f3eec100f7d'))
    # print(reference==out)
