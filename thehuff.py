
# No one hassels with The Huff
# Mathias Olsson 2016

# This is a very simple implementation of Canonical Huffman Encoding
# I made it to learn how Huffman Encoding and Canonical Huffman Encoding works

import sys
import struct
import argparse

import bitstring

def encode(inputfile, outputfile):
    '''
    Huffman encode a file.
    '''
    # 1. First we must find the frequency of each symbol in the alphabet
    # I define the alphabet as bytes from 0 to 255
    frequency = {}

    with open(inputfile,"rb") as f:
        data = bytearray(f.read())

    for byte in data:
        # Do stuff with byte.
        key = byte
        if frequency.has_key(key):
            frequency[key] += 1
        else:
            frequency[key] = 1

    # 2. Put the frequency and the value in a queue.
    # Also create an empty queue to be used later
    # We must always make sure that our queue is sorted by frequency
    # so that we can easily find the nodes with the lowest frequency.
    # I use a Tree node to store the data
    class Tree:
        def __init__(self, frequency, value, left = None, right = None):
            self.frequency = frequency
            self.value = value
            self.left = left
            self.right = right
            
        def __lt__(self, other):
            return self.frequency <= other.frequency

    queue = []
    merge_queue = []

    for key, value in frequency.iteritems():
        value = frequency[key]
        node = Tree(value, key)
        queue.append(node)

    queue.sort(reverse=True)

    for t in queue:
        print "frequency: %s key: %s" % (t.frequency, t.value)

    # 3. Now remove the two Tree nodes with the lowest frequencies.
    # Examine both queues but prefare the queue with single elements.
    # Create a new node with them as children and the sum of their
    # frequencies as new frequency. Put the new node into the queue
    # and sort the queue.
    # Repeat until there is only one element in the queue.
    # The last element is the root of our tree
    while len(queue) > 0 or len(merge_queue) > 1:
        if len(merge_queue) > 0:
            if (len(queue) > 0):
                if merge_queue[-1].frequency < queue[-1].frequency:
                    left = merge_queue.pop()        
                else:
                    left = queue.pop()        
            else:
                left = merge_queue.pop()        
        else:
            left = queue.pop()        

        if len(merge_queue) > 0:
            if len(queue) > 0:
                if merge_queue[-1].frequency < queue[-1].frequency:
                    right = merge_queue.pop()        
                else:
                    right = queue.pop()                
            else:
                right = merge_queue.pop()        
        else:
            right = queue.pop()

        print "left frequency: %s key: %s" % (left.frequency, left.value)
        print "right frequency: %s key: %s" % (right.frequency, right.value)
        
        node = Tree(left.frequency + right.frequency, str(left.value) + ":" + str(right.value), left, right)
        merge_queue.append(node)
        # TODO Use insertion sort instead
        merge_queue.sort(reverse=True)

    # get our tree
    tree = merge_queue.pop()
    print "root frequency: %s key: %s" % (tree.frequency, tree.value)

    def print_codes(node, code = ""):
        if node.left == None and node.right == None:
            print "Value: %s %s Code: %s Length: %s" % (node.value, chr(int(node.value)), code, len(code))
        else:
            print_codes(node.left, code + "0")
            print_codes(node.right, code + "1")

    print_codes(tree)

    # At this point we are done.
    # BUT we want Canonical Huffman so ...

    # Now we must build the canonical codes
    # We don't need the tree, just the code length and the value
    # Then we must sort on length and value

    # This part is almost identical to the RFC for Deflate

    # 1. Find the length of each code = depth of tree for this leaf
    # I use a recursive function for that
    code_lengths = []

    def build_code_lengths(node, code = 0):
        if node.left == None and node.right == None:
            item = (code, node.value)
            code_lengths.append(item)
        else:
            build_code_lengths(node.left, code + 1)
            build_code_lengths(node.right, code + 1)

    build_code_lengths(tree)
    # 2. Sort on code length and value
    code_lengths.sort()

    for t in code_lengths:
        print "length: %s value: %s" % t

    # 3. Find how many codes have the same length for each length
    bitlength_count = {}
    for t in code_lengths:
        length = t[0]
        if bitlength_count.has_key(length):
            bitlength_count[length] += 1
        else:
            bitlength_count[length] = 1

    for key, value in bitlength_count.iteritems() :
        print "a", key, value
        
    # 4. Find the first code for each length
    next_code = {}
    code = 0
    bitlength_count[0] = 0
    for bits in range(1,16):
        if not bitlength_count.has_key(bits-1):
            bitlength_count[bits-1] = 0
        code = (code + bitlength_count[bits-1]) << 1
        next_code[bits] = code

    for key, value in bitlength_count.iteritems() :
        print "b", key, value

    for key, value in next_code.iteritems() :
        print "c", key, bin(value)

    # 5. Assign codes
    codes = []
    for n in range(0,len(code_lengths)):
        length = code_lengths[n][0]
        value = code_lengths[n][1]
        if length != 0:
            item = (value, next_code[length])
            codes.append(item)
            next_code[length] += 1
            
    value_table = bytearray()
    code_length_table = bytearray()
    mapping = {}
    for t in codes:
        mapping[t[0]] = t[1]
        value = t[0]
        code = bin(t[1])

        value_table.append(value)
        code_length_table.append(len(code)-2) # -2 for 0b

        print "value: %s %s code: %s" % (value, chr(int(value)), code)

    if len(value_table) > 256:
        print "More than 256 different values. Should not happen"
        sys.exit(-1)

    print "value_table:"
    for byte in value_table:
        print "%d" % (byte)

    print "code_length_table:"
    for byte in code_length_table:
        print "%d" % (byte)

    print "mapping: %s" % (mapping)

    # Encoding
    bits = bitstring.BitArray()
    for byte in data:
        code = bin(mapping[byte])
        bits.append(code)

    bytar = bits.tobytes()
    with open(outputfile, "wb") as f:
        f.write(struct.pack('B', len(value_table)))
        f.write(value_table)
        f.write(code_length_table)
        f.write(bytar)

def decode(inputfile, outputfile):
    '''
    Huffman decode a file
    '''
    # Decoding
    with open(inputfile, "rb") as f:
        encoded_bytes = bytearray(f.read())

    number_of_symbols = encoded_bytes.pop(0)
    print "num_symbols: %s" % (number_of_symbols)

    decode_symbol_table = []
    for i in range(0, number_of_symbols):
        symbol = encoded_bytes.pop(0)
        decode_symbol_table.append(symbol)

    print "decoded symbol table: %s" % (decode_symbol_table)

    decode_code_length_table = []
    for i in range(0, number_of_symbols):
        code_length = encoded_bytes.pop(0)
        decode_code_length_table.append(code_length)

    print "decoded code length table: %s" % (decode_code_length_table)

    # Rebuild tree
    decode_code_table = {}
    code = 0
    for i in range(0, len(decode_symbol_table)):
        symbol = decode_symbol_table[i]
        print "symbol: %s code: %s" % (symbol, bin(code))
        decode_code_table[code] = symbol
        if i < len(decode_symbol_table)-1: 
            code = (code + 1) << (decode_code_length_table[i+1] - decode_code_length_table[i])

    decode_code_max_len = decode_code_length_table[-1]

    encoded_bits = bitstring.BitArray(encoded_bytes)

    decoded_data = bytearray()

    start_pos = 0
    while start_pos < len(encoded_bits):
        found = False
        for i in range(1, decode_code_max_len+1):
            bits_to_analyze = encoded_bits[start_pos:start_pos+i]
            code = bits_to_analyze.uint
            if decode_code_table.has_key(code):
                symbol = decode_code_table[code]
                decoded_data.append(symbol)
                start_pos += i
                found = True
                break

        if not found:
            print "decode failed, startpos %s" % (start_pos)
            print "decoded code table: %s" % (decode_code_table)
            print "decode_code_max_len %s" % (decode_code_max_len)
            sys.exit(-2)
            break

    with open(outputfile, "wb") as f:
        f.write(decoded_data)


# Parse command line arguments
parser = argparse.ArgumentParser(description='Huffman encode and decode a file')
parser.add_argument('infile', help='Inputfile')
parser.add_argument('outfile', help='Outputfile')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--encode', help='Encode', action='store_true')
group.add_argument('--decode', help='Decode', action='store_true')
parser.add_argument('--verbose', help='Print debug stuff', action='store_true')

args = parser.parse_args()

input_file = args.infile
output_file = args.outfile

if args.encode:
    encode(input_file, output_file)

if args.decode:
    decode(input_file, output_file)
