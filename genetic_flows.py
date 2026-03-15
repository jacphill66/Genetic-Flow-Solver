import networkx as nx
import random
import utils
import copy

def parse_ground_truths(ground_truths):
    lines = ground_truths.split("\n")
    paths = []
    flows = []
    for p in lines:
        if not p.isspace() and p != "":
            p = p.split()
            paths.append(p[1:])
            flows.append(p[0])
    return paths, flows

def build_flow_from_ground_truths(paths, min_flow, max_flow, weights=None):
    if weights != None and len(weights) != len(paths):
        raise Exception("Number of Paths must Match Number of Weights!")
        
    if weights == None:
        weights = []
                           
        for i in range(0, len(paths)):
            weights.append(random.randrange(min_flow, max_flow+1))

    g = nx.DiGraph()
    
    path_index = 0
    for p in paths:
        for i in range(len(p)-1):
            if not g.has_edge(p[i], p[i+1]):
                g.add_edge(p[i], p[i+1], flow=[weights[path_index]])
            else:
                g[p[i]][p[i+1]]["flow"][0] += weights[path_index]
        path_index += 1
    return g
   
def initialize_flow(ground_truths, min_flow=1, max_flow=100, check_if_valid=False, weights=None):
    """
    Takes a description of a flow network. Currently, a set of ground truth paths and generates a flow graph based on them.
    """
    paths = parse_ground_truths(ground_truths)
    flow = build_flow_from_ground_truths(paths[0], min_flow, max_flow, weights)
    
    if check_if_valid:
        utils.check_valid_multi_flow(flow, 1)
        
    return flow

def greedily_decompose_flow(flow_network, weighted_paths=None, copy_network=True):
    """
    Decomposes a network flow using a version of greedy width. We may change this to a more efficient solution.
    """
    if weighted_paths == None:
        weighted_paths = []
    if copy_network:
        flow_network = copy.deepcopy(flow_network)
    current_source = '0'
    sink = str(len(flow_network.nodes)-1)
    path_count = 0
    
    curr_path_weight = float('inf')
    current_path = []
    while True:
        # Copy because we modify the edge flows
        edges = flow_network.edges(current_source)

        highest_flow_edge = None
        highest_flow = -1
            
        # Greedily choose the highest flow path
        for u,v in edges:
            flow = flow_network[u][v]['flow'][0]
            if flow > highest_flow:
                highest_flow = flow
                highest_flow_edge = (u, v) 
        
        # When every edge out has remaining flow 0, the flow is decomposed
        if highest_flow == 0:
            return weighted_paths, path_count
        
        # Path weight is the smallest flow of the path
        if highest_flow < curr_path_weight:
            curr_path_weight = highest_flow
        
        # Add the edge to the path
        u = highest_flow_edge[0]
        v = highest_flow_edge[1]
        current_path.append((u,v))
        
        # Move onto the next edge
        current_source = v
            
        # If the current path is complete (source-to-sink) restart
        if current_source == sink:  
        
            # Adjust the remaining flow values to account for the path
            for u,v in current_path:
                flow_network[u][v]["flow"][0] -= curr_path_weight
                
            # Store the path
            weighted_paths.append((current_path, curr_path_weight))
            
            # Reset everything
            curr_path_weight = float('inf')
            current_path = []
            path_count += 1
            current_source = '0'        
    
    # It should return midway through when the flow is decomposed or invalid
    raise Exception("Shouldn't be Here!")

def take_random_path(flow_network):
    # Flow network is assumed to be a copy; this mutates the graph's flow values
    current_source = '0'
    sink = str(len(flow_network.nodes)-1)
    
    curr_path_weight = float('inf')
    path = []
    while True:        
        edges = list(flow_network.edges(current_source))
        chosen_edge = None
        chosen_flow = 0
        
        # Iterate through the edges in random order with no repeats
        for e in random.sample(range(0, len(edges)), k=len(edges)):
            chosen_edge = (edges[e][0], edges[e][1])
            chosen_flow = flow_network[chosen_edge[0]][chosen_edge[1]]['flow'][0]
            
            # Take the first non-zero edge
            if chosen_flow != 0:
                break
        
        # If the flow is 0 you can't find a path
        if chosen_flow == 0:
            return None, None
        
        # Path weight is the flow of the edge with lowest flow of the path
        if chosen_flow < curr_path_weight:
            curr_path_weight = chosen_flow
        
        # Add the current edge to the path
        u = chosen_edge[0]
        v = chosen_edge[1]
        path.append((u,v))
        
        # Move onto the next edge
        current_source = v
            
        # If the current path is complete (source-to-sink) adjust the network
        if current_source == sink:  
            
            # Adjust the flow values of the edges used by the path
            for u,v in path:
                flow_network[u][v]["flow"][0] -= curr_path_weight
            
            return path, curr_path_weight

def randomly_decompose_flow(flow_network, weighted_paths=None, copy_network=True):
    """
    Decomposes a network flow using a version of greedy width. We may change this to a more efficient solution.
    """
    if weighted_paths == None:
        weighted_paths = []
    if copy_network:
        flow_network = copy.deepcopy(flow_network)
    path_count = 0
    
    curr_path_weight = float('inf')
    current_path = []
    while True:   
        path, weight = take_random_path(flow_network)
        if path == None:
            return weighted_paths, path_count
            
        path_count += 1            
        weighted_paths.append((path, weight))
        
    # It should return midway through when the flow is decomposed or invalid
    raise Exception("Shouldn't be Here!")
    
def generate_decompositions(flow_network, quantity, random_percentage=-1.0):
    decomps = []
    
    count = 0
    while count < quantity:
        flow_copy = copy.deepcopy(flow_network)
        if random.random() > random_percentage:  
            # It should be a param for how many random paths to take
            path, path_weight = take_random_path(flow_copy)
            decomposition, num_paths = greedily_decompose_flow(flow_copy, copy_network=False)
            decomposition.append((path, path_weight))
            num_paths += 1
            decomps.append((flow_copy, decomposition, num_paths))
        else:
            decomposition, num_paths = randomly_decompose_flow(flow_copy, copy_network=False)
            decomps.append((flow_copy, decomposition, num_paths))
        count += 1
    return decomps

def remove_path(flow_network, path, weight):
    for (u,v) in path:
        flow_network[u][v]["flow"][0] += weight

def fitness():
    pass

def mutate_decomposition(flow_network, decomposition, mutation_strength=0.1, smart_mutation=False):
    if len(decomposition) < mutation_strength:
        raise Exception("The Size of the Decomposition Must be >= Mutation Strengh!")
    number_of_paths = int(mutation_strength * len(decomposition))
    for i in range(0, number_of_paths):
        # p, w = decomposition.pop()
        p, w = decomposition.pop(random.randrange(len(decomposition)))
        remove_path(flow_network, p, w)
    d = None
    num_paths = None
    
    if smart_mutation:
        d, num_paths = randomly_decompose_flow(flow_network, weighted_paths=decomposition, copy_network=False)
    else:
        d, num_paths = greedily_decompose_flow(flow_network, weighted_paths=decomposition, copy_network=False)
    return flow_network, d, len(decomposition)+num_paths

def select_new_population(population, pop_size, tournament_size=2, victor_size=1):
    new_pop = []
    for i in range(0, pop_size):
        new_pop.append(None)
    new_pop_size = 0
    while new_pop_size < pop_size:
        individuals = []
        for i in range(0, tournament_size):
            individuals.append(None)
                
        for i in range(0, tournament_size):
            random_individual = random.choice(population)
            index = 0
            # Insert it in order (this assumes a simple fitness function using just the number of paths)
            
            j = 0
            while individuals[j] != None and individuals[j][2] >= random_individual[2]:
                j += 1

            while individuals[j]  != None:
                t = individuals[j]
                individuals[j] = random_individual[2]
                j += 1

            individuals[j] = random_individual[2]
                                
        for i in range(0, victor_size):
            new_pop[new_pop_size + i] = individuals.pop()
        new_pop_size += victor_size
    return new_pop   
    
def evolve(flow_network, pop_size, generations, tournament_size=2, victor_size=1, mutation_chance=0.1, mutation_strength=2, random_percentage=-1.0, smart_mutate=False):
    pop = generate_decompositions(flow_network, pop_size, random_percentage)
    
    min_paths = pop[0][2]
    avg = 0
    for p in pop:
        if p[2] < min_paths:
            min_paths = p[2]
            print(f"New Min Found:{p[2]}")
        avg += p[2]
    og_min_paths = min_paths
    print(f"Average Paths {avg/pop_size} for Generation: {0}")
    og_avg = avg/pop_size
    for i in range(0, generations):
        for j in range(0, len(pop)):
            if random.random() < mutation_chance:
                x = copy.deepcopy(pop[j])
                pop[j] = mutate_decomposition(x[0], x[1], mutation_strength, smart_mutate)
        pop = select_new_population(pop, pop_size, tournament_size, victor_size)    

        avg = 0
        for p in pop:
            if p[2] < min_paths:
                min_paths = p[2]
                print(f"New Min Found:{p[2]}")
            avg += p[2]
        print(f"Average Paths {avg/pop_size} for Generation: {i+1}")
    print(f"Minimum Paths: {min_paths}")
    print(f"Improvement:{og_avg-min_paths}")
    print(f"Improvements from Initial Population:{og_min_paths-min_paths}")
    return pop, min_paths
    
def cross_over():
    # pick one path at a time from each flow up until the crossover percentage is met
    # ensure the new path is consistent with existing paths
    pass

def fitness():
    pass

def compare_paths(p1, p2):
    if len(p1) != len(p2):
        return False
    for (e1, e2) in zip(p1, p2):
        if e1 != e2:
            return False
    return True
    
def compare_weighted_paths(p1, w1, p2, w2):
    if w1 != w2:
        return False
    return compare_paths(p1, p2)

def compare_decompositions(d1, d2, include_weights=False):
    shared_paths = 0
    d1_unique_paths = 0
    d2_unique_paths = 0
    d1_total_paths = 0
    d2_total_paths = 0
    
def original_weighted_paths_decomp():
    # return the original weighted paths as a decomp
    pass

def validate_decomposition():
    # ensure a decomp is valid
    pass

if __name__ == "__main__":
    truths_1 = """
        105 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 
        132 0 2 3 4 5 6 7 8 9 10 11 12 13 14 16 17 19 21 22 25 
        393 0 3 4 5 6 7 8 9 10 11 12 13 14 16 17 18 19 21 22 23 25 
    """
    
    truths_2 = """
        46 0 1 2 3 4 5 6 7 8 9 10 11 14 15 16 19 21 22 25 28 31 32 33 36 
        93 0 1 2 3 4 5 6 7 8 9 10 11 12 15 16 19 21 22 25 28 29 30 31 32 33 36 
        580 0 1 2 3 4 5 6 7 8 9 10 11 12 15 16 19 21 22 25 26 27 28 31 32 33 34 36 
        15 0 2 3 4 5 6 7 8 9 10 11 12 15 16 19 21 22 25 28 31 32 33 34 35 36 
        323 0 3 4 5 7 8 9 10 11 12 13 36 
        2 0 4 5 6 7 8 9 10 11 12 15 17 19 21 22 25 28 31 36 
        97 0 4 5 6 7 8 9 10 11 15 16 18 19 21 22 25 28 31 36 
        74 0 4 5 7 8 9 10 11 12 14 15 16 19 21 22 25 28 31 36 
        18 0 4 5 6 7 8 9 10 11 12 15 16 19 21 22 23 24 25 28 31 36 
        329 0 4 5 6 7 8 9 10 11 12 15 16 19 21 22 23 25 28 31 32 36 
        241 0 4 5 6 7 8 9 10 11 12 15 19 20 21 22 25 28 31 32 33 36 
        1 0 4 5 6 7 8 9 10 11 12 15 16 17 19 20 21 22 25 28 31 32 33 36 
    """

    truths_3 = """
        725 0 1 2 4 5 6 7 8 9 10 11 12 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 34 35 36 37 43 44 45 46 
        66 0 3 4 5 6 7 8 9 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 29 32 34 35 36 46 
        253 0 19 20 21 22 23 24 25 26 27 28 29 40 41 46 
        690 0 21 22 23 24 25 26 27 29 32 33 35 46 
        2 0 22 23 24 25 26 27 28 29 33 34 35 36 37 38 46 
        799 0 23 24 25 26 27 28 29 32 39 46 
        1000 0 24 25 26 27 29 30 31 34 35 36 37 44 46 
        470 0 26 27 28 29 30 31 33 34 35 36 37 38 46 
        793 0 31 32 33 34 35 36 37 40 42 46 
    """

    # Params to play around with
    weights = None     # Weights must be None or a list of integers whose length = # ground truth paths
    population = 1000   # Number of initial solutions to consider
    generations = 100  # Number of generations
    mutation_chance=0.1 # chance of mutating a solution
    mutation_strength=0.4 # How strong is a mutation (percentage of paths mutated)

    
    flow = initialize_flow(truths_3, weights=weights)
    greedy_decomposition, path_count = greedily_decompose_flow(flow, copy_network=True)
    
    res, min_paths = evolve(flow, population, generations, tournament_size=2, victor_size=1, mutation_chance=mutation_chance, mutation_strength=mutation_strength, random_percentage=-1.0, smart_mutate=False)
    
    print(f"Our Algo: {min_paths}, Greedy Decomp: {path_count}")

"""
the population is improving, but its really just being dominated by the best individuals
the best solution isn't improving

Things to work on:
better diversify the population
add crossover
make mutation better
prevent early convergence
ensure more diversity
fix/optimize selection
check everything works
"""