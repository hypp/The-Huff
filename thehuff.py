
# No one hassels with The Huff
# Mathias Olsson 2016

# This is a very simple implementation of Canonical Huffman Encoding
# I made it to learn how Huffman Encoding and Canonical Huffman Encoding works

# 1. First we must find the frequency of each symbol in the alphabet
# I define the alphabet as bytes from 0 to 255
frequency = {}

with open("clearscreen.ROM","rb") as f:
    byte = f.read(1)
    while byte:
        # Do stuff with byte.
        key = str(ord(byte))
        if frequency.has_key(key):
            frequency[key] += 1
        else:
            frequency[key] = 1
        byte = f.read(1)

# 2. Put the frequency and the value in a queue.
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

for key, value in frequency.iteritems() :
    value = frequency[key] 
    node = Tree(value,key)
    queue.append(node)
    
queue.sort(reverse=True)
        
for t in queue:
    print "frequency: %s key: %s" % (t.frequency, t.value)

# 3. Now remove the two Tree nodes with the lowest frequencies
# and create a new node with them as children and the sum of their
# frequencies as new frequency. Put the new node into the queue
# and sort the queue.
# Repeat until there is only one element in the queue.
# The last element is the root of our tree
while len(queue) > 1:
    left = queue.pop()
    right = queue.pop()

    print "left frequency: %s key: %s" % (left.frequency, left.value)
    print "right frequency: %s key: %s" % (right.frequency, right.value)
    
    node = Tree(left.frequency + right.frequency, left.value + ":" + right.value, left, right)
    queue.append(node)
    # TODO Use insertion sort instead
    queue.sort(reverse=True)

# get our tree
tree = queue.pop()
print "root frequency: %s key: %s" % (tree.frequency, tree.value)

def print_codes(node, code = ""):
    if node.left == None:
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
    if node.left == None:
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
        
for t in codes:
    value = t[0]
    code = bin(t[1])
    print "value: %s %s code: %s" % (value, chr(int(value)), code)

