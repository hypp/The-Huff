
frequency = {}

with open("test.txt","rb") as f:
    byte = f.read(1)
    while byte:
        # Do stuff with byte.
        key = str(ord(byte))
        if frequency.has_key(key):
            frequency[key] += 1
        else:
            frequency[key] = 1
        byte = f.read(1)

class Tree:
    def __init__(self, frequency, value, left = None, right = None):
        self.frequency = frequency
        self.value = value
        self.left = left
        self.right = right
        
    def __lt__(self, other):
        return self.frequency <= other.frequency

queue = []

for key in range(0, 256):
    key = str(key)
    if frequency.has_key(key):
        value = frequency[key] 
        node = Tree(value,key)
        queue.append(node)
    
queue.sort(reverse=True)
        
for t in queue:
    print "frequency: %s key: %s" % (t.frequency, t.value)

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
