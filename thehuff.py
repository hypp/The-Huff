
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
    # Examine both queues but prefer the queue with single elements.
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

    def build_code_lengths(node, length = 0):
        if node.left == None and node.right == None:
            item = (length, node.value)
            code_lengths.append(item)
        else:
            build_code_lengths(node.left, length + 1)
            build_code_lengths(node.right, length + 1)

    build_code_lengths(tree)
    # 2. Sort on code length and value
    code_lengths.sort()

    for t in code_lengths:
        print "length: %s value: %s" % t

    # 3. Find how many codes have the same length for each length
    # 4. New impl. Find the code for each symbol
    encode_code_table = {}
    mapping = {}    
    code = 0
    for i in range(0, len(code_lengths)):
        length, symbol = code_lengths[i]
        print "symbol: %s code: %s length: %s" % (symbol, bin(code), length)
        encode_code_table[code] = (symbol, length)
        mapping[symbol] = (code, length)
        if i < len(code_lengths)-1:
            code = (code + 1) << (code_lengths[i+1][0] - code_lengths[i][0])


    print "encode_code: %s" % (encode_code_table)

    value_table = bytearray()
    code_length_table = bytearray()
    for i in range(0, len(code_lengths), 2):
        length1, value1 = code_lengths[i]
        value_table.append(value1)
        if i+1 >= len(code_lengths):
            length2 = 1
            value2 = -1
        else:
            length2, value2 = code_lengths[i+1]
            value_table.append(value2)

        if length1 > 16 or length1 < 1:
            print "Invalid length1. Fail %s" % (length1)
            sys.exit(1)

        if length2 > 16 or length2 < 1:
            print "Invalid length2. Fail %s" % (length2)
            sys.exit(1)

        packed_code = (length1-1) << 4 | (length2-1)
        code_length_table.append(packed_code)

        print "value1: %s %s code: %s" % (value1, chr(int(value1)), hex(length1))
        print "value2: %s %s code: %s %s" % (value2, chr(int(value2)), hex(length2), hex(packed_code))

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
        code, length = mapping[byte]
        str_code = "0b{code:0{width}b}".format(code=code, width=length)
        bits.append(str_code)

    bytar = bits.tobytes()
    print "Length values: %s" % (len(value_table))
    print "Length code lengths: %s" % (len(code_length_table))
    print "Length data: %s" % (len(bytar))
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
    for i in range(0, number_of_symbols/2):
        code_length = encoded_bytes.pop(0)
        cl1 = ((code_length & 0xf0) >> 4) + 1
        cl2 = (code_length & 0xf) + 1
        print "packed_code: %s %s %s" % (hex(code_length), hex(cl1), hex(cl2))
        decode_code_length_table.append(cl1)
        decode_code_length_table.append(cl2)

    print "decoded code length table: %s" % (decode_code_length_table)

    # Rebuild tree
    decode_code_table = {}
    code = 0
    for i in range(0, len(decode_symbol_table)):
        symbol = decode_symbol_table[i]
        length = decode_code_length_table[i]
        str_code = "0b{code:0{width}b}".format(code=code, width=length)
        print "symbol: %s code: %s" % (symbol, str_code)
        decode_code_table[str_code] = symbol
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
            str_code = "0b{code:0{width}b}".format(code=code, width=i)
            if decode_code_table.has_key(str_code):
                symbol = decode_code_table[str_code]
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
