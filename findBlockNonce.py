#!/bin/python
import hashlib
import os
import random


def mine_block(k, prev_hash, rand_lines):
    """
        k - Number of trailing zeros in the binary representation (integer)
        prev_hash - the hash of the previous block (bytes)
        rand_lines - a set of "transactions," i.e., data to be included in this block (list of strings)

        Finds a nonce such that the SHA256 hash of prev_hash + rand_lines + nonce 
        has at least k trailing zeros in its binary representation.
    """
    if not isinstance(k, int) or k < 0:
        print("mine_block expects positive integer")
        return b'\x00'

    # Convert `rand_lines` into a single string and then encode it as bytes
    transactions = ''.join(rand_lines).encode('utf-8')
    
    # Target ending in k zeros in binary form
    target_suffix = '0' * k
    
    nonce = 0  # Start nonce from 0 and increment to find a valid one
    while True:
        # Convert nonce to bytes
        nonce_bytes = str(nonce).encode('utf-8')
        
        # Concatenate previous hash, transactions, and the nonce
        combined_data = prev_hash + transactions + nonce_bytes
        
        # Compute SHA256 hash
        hash_result = hashlib.sha256(combined_data).hexdigest()
        
        # Convert hash to binary form
        binary_hash = bin(int(hash_result, 16))[2:].zfill(256)  # zfill for full 256-bit length

        # Check if last `k` bits are zeros
        if binary_hash[-k:] == target_suffix:
            return nonce_bytes  # Return the nonce in bytes format

        # Increment nonce and try again
        nonce += 1

def get_random_lines(filename, quantity):
    """
    This is a helper function to get the quantity of lines ("transactions")
    as a list from the filename given. 
    Do not modify this function
    """
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line.strip())

    random_lines = []
    for x in range(quantity):
        random_lines.append(lines[random.randint(0, quantity - 1)])
    return random_lines


if __name__ == '__main__':
    # This code will be helpful for your testing
    filename = "bitcoin_text.txt"
    num_lines = 10  # The number of "transactions" included in the block

    # The "difficulty" level. For our blocks this is the number of Least Significant Bits
    # that are 0s. For example, if diff = 5 then the last 5 bits of a valid block hash would be zeros
    # The grader will not exceed 20 bits of "difficulty" because larger values take to long
    diff = 20

    rand_lines = get_random_lines(filename, num_lines)
    nonce = mine_block(diff, rand_lines)
    print(nonce)
