import threading
import math
import sys
from queue import Queue
import copy
import time

# Function to get node ID from node name
def get_node_id(name):
    return (ord(name) - 65)

# Function to get node name from node ID
def get_node_name(num):
    return chr(num + 65)

# Class representing a router
class Router:
    def __init__(self, name):
        self.name = name
        self.id = get_node_id(name)
        self.fwd = dict([(i, math.inf) for i in range(no_of_nodes)])  # Initialize forwarding table with infinity
        self.fwd[self.id] = -1  # Cost to self is set to -1
        self.next_hop = [-1 for i in range(no_of_nodes)]  # Initialize next hop for each destination to -1
        self.neighbors = []  # List to store neighboring routers
        self.updated = []  # List of nodes whose forwarding table was updated in the previous iteration

# Bellman-Ford algorithm implementation
def Bellman_Ford(routers, i):
    temp_fwd = copy.deepcopy(routers[i].fwd)  # Create a copy of the forwarding table
    while not queueList[i].empty():  # While there are items in the queue
        next_fwd = queueList[i].get()  # Get the next forwarding table from the queue
        received_from = -1

        # Find out from which router the current forwarding table was received
        for j in range(no_of_nodes):
            if next_fwd[j] == -1:
                received_from = j

        # Update the forwarding table based on received information
        for j in range(no_of_nodes):
            if j != received_from:
                if temp_fwd[j] > routers[i].fwd[received_from] + next_fwd[j]:
                    temp_fwd[j] = routers[i].fwd[received_from] + next_fwd[j]
                    routers[i].next_hop[j] = received_from

        # Store updated destinations
        for j in range(no_of_nodes):
            if routers[i].fwd[j] != temp_fwd[j]:
                routers[i].updated.append(j)

    routers[i].fwd = dict(temp_fwd)  # Update the forwarding table

# Function to propagate forwarding tables to neighbors
def Propagate(routers, i):
    
    # Wait for 2 seconds
    time.sleep(2)
    
    # Send the forwarding table to all neighboring routers
    for neighbor in routers[i].neighbors:
        queueList[neighbor].put(copy.deepcopy(routers[i].fwd))

    # Wait until the queue is full
    while True:
        if queueList[i].full():
            break

    # Perform Bellman-Ford algorithm for the router
    Bellman_Ford(routers, i)

    # Clear the queue after propagation
    queueList[i].queue.clear()

# Main function
if __name__ == '__main__':
    if(len(sys.argv) != 2):
        print("Usage: python dvr.py <input_file>")
        sys.exit(0)

    input_file = sys.argv[1]
    with open(input_file, "r") as f:
        no_of_nodes = int(f.readline())  # Read the number of nodes
        nodes = f.readline().split()  # Read the names of nodes
        routers = [Router(node) for node in nodes]  # Create router objects for each node
        line = f.readline()
        while line != "EOF":
            from_edge, to_edge, weight = line.split()  # Read edge information
            # Update forwarding tables and neighbor information for both routers connected by the edge
            routers[get_node_id(from_edge)].fwd[get_node_id(to_edge)] = int(weight)
            routers[get_node_id(from_edge)].neighbors.append(get_node_id(to_edge))
            routers[get_node_id(from_edge)].next_hop[get_node_id(to_edge)] = get_node_id(to_edge)
            sorted(routers[get_node_id(from_edge)].neighbors)

            routers[get_node_id(to_edge)].fwd[get_node_id(from_edge)] = int(weight)
            routers[get_node_id(to_edge)].neighbors.append(get_node_id(from_edge))
            routers[get_node_id(to_edge)].next_hop[get_node_id(from_edge)] = get_node_id(from_edge)
            sorted(routers[get_node_id(to_edge)].neighbors)
            line = f.readline()

    queueList = [Queue(maxsize = len(routers[i].neighbors)) for i in range(no_of_nodes)]  # Create queues for each router

    # Print initial routing tables
    print("\nInitial Routing Tables:")
    print_str = ""
    for i in range(no_of_nodes):
        print_str += f"\nRouting table of router {routers[i].name}:"
        print_str += f"\nDestination       Cost"
        for key, item in routers[i].fwd.items():
            if key != i:
                print_str += "\n" + "   " + str(get_node_name(key)) + "    ----->     " + str(item)
            else:
                print_str += "\n" + "   " + str(get_node_name(key)) + "    ----->     " + str(0)
    print(print_str)

    # Run iterations of Bellman-Ford algorithm
    for k in range(4):
        for i in range(no_of_nodes):
            thread = threading.Thread(target = Propagate, args = (routers, i))  # Create thread for each router
            thread.start()  # Start the thread
        thread.join()  # Wait for all threads to finish

        # Print routing tables after each iteration
        print("==================================================")
        print("                  Iteration:" + str(k + 1))
        print("==================================================")

        print_str = ""
        for i in range(no_of_nodes):
            print_str += f"\nRouting table of router {routers[i].name}:"
            print_str += f"\n  Destination          Cost          Next Hop"
            for key, item in routers[i].fwd.items():
                if key != i:
                    print_str += "\n"
                    if key in routers[i].updated:
                        print_str += "  *"
                    print_str += "\t" + str(get_node_name(key)) + "    ----->     " + str(item)
                    print_str += "    ----->     " + str(get_node_name(routers[i].next_hop[key]))
                else:
                    print_str += "\n" + "\t" + str(get_node_name(key)) + "    ----->     " + str(0)
                    print_str += "    ----->     " + str(get_node_name(i))
            routers[i].updated.clear()
        print(print_str + "\n\n")