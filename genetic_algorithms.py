import copy
import random

def correct_columns(board):
    correct_columns = 0
    column = []
    for c in range(0, 9):
        for r in range(0, 9):
            column.append(board[r][c])
        
        if 9 - len(set(column)) == 0:
            correct_columns += 1
            
        column = []
    return correct_columns

def correct_3_by_3s(board):
    row_offset = 0
    column_offset = 0
    correct_cells = 0
    for a in range(0, 3):
        column_offset = 0
        for b in range(0, 3):
            cell_elements = []
            for i in range(0, 3):
                for j in range(0, 3):
                    cell_elements.append(board[row_offset+i][column_offset+j])
        
            if len(set(cell_elements)) - 9 == 0:
                correct_cells += 1
            
            column_offset += 3
        row_offset += 3
    return correct_cells

def fitness(board):
    return correct_columns(board) + correct_3_by_3s(board)

def generate_board():
    return [random.sample(range(1, 10), k=9) for i in range(9)]

def generate_initial_population(size):
    population = []
    for i in range(0, size):
        population.append(generate_board())
    return population
    
def find_best_in_pop(pop):
    best_individual = None
    best_fitness = 0
    for i in pop:
        f = fitness(i)
        if fitness(i) > best_fitness:
            best_fitness = f
            best_individual = i
    return best_individual, best_fitness

def mutate(board):
    row = random.randrange(9)
    item1 = random.randrange(9)
    item2 = random.randrange(9)

    new_row = board[row]
    i = new_row[item1]
    j = new_row[item2]
    new_row[item1] = j
    new_row[item2] = i
    board[row] = new_row

def crossover(b1, b2):
    new_board = []
    new_board.append(b1[0][:])
    new_board.append(b1[1][:])
    new_board.append(b1[2][:])
    new_board.append(b1[3][:])
    new_board.append(b1[4][:])
    new_board.append(b2[5][:])
    new_board.append(b2[6][:])
    new_board.append(b2[7][:])
    new_board.append(b2[8][:])
    return new_board
    
def evolve(pop_size, generations, mutation_rate=0.1, crossover_rate=0.75, tournament_size=5, victor_size=3):
    pop = sorted(generate_initial_population(pop_size), key=fitness)
    # Sort the population by fitness

    for i in range(0, generations):
        new_pop = [None] * pop_size
        
        j = 0
        while j < pop_size:
            competitors = []
            for a in range(0, tournament_size):
                competitors.append(random.choice(pop))
            competitors = sorted(competitors, key=fitness)
                        
            victors = []
            for a in range(0, victor_size):
                victors.append(competitors.pop())
            
            k = 0
            while k < len(victors)-1 and j < pop_size:
                new_pop[j] = victors[k]
                j += 1
                
                if j < pop_size and random.random() < crossover_rate:
                    new_pop[j] = crossover(victors[k], victors[k+1])
                    j += 1
                    
                if random.random() < mutation_rate:
                    new_pop[j] = mutate(victors[k])
                
                k += 1           

        board, f = find_best_in_pop(new_pop)
        print(f"Best Fitness: {f} at Generation: {i}")
          
evolve(1000, 1000, 0.01)