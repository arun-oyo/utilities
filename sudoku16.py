# This program works by identifying the remaining elements and backtrack only on thoese.
# The elements are inserted in the increasing order of the elements left to be inserted. And hence runs much faster.
# Comparing with other back tracking algorithms, it runs 5X faster.

ELEMENTS = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G']
MATRIX_SIZE= len(ELEMENTS)
BLOCK_SIZE=4
EMPTY_CELL='0'

# Input matrix
arr = [
	['E','F','4','0','B','G','0','0','1','0','A','0','6','3','2','D'],
	['0','1','0','5','F','8','0','0','E','6','0','3','0','G','0','0'],
	['8','0','0','A','0','0','0','9','0','B','7','0','E','C','4','0'],
	['0','0','6','0','3','0','4','0','0','2','0','0','0','8','0','0'],
	['0','7','9','B','0','4','D','3','0','0','8','0','0','6','F','0'],
	['0','5','0','0','0','0','6','8','9','0','0','4','B','0','D','7'],
	['0','0','A','8','7','5','9','B','0','0','G','0','C','4','3','E'],
	['0','3','0','0','2','0','F','0','D','0','0','0','0','5','0','9'],
	['0','0','D','0','0','0','G','0','4','0','9','0','F','B','E','1'],
	['1','0','2','G','C','0','0','0','8','0','0','F','0','D','9','5'],
	['0','4','0','0','0','9','A','F','B','D','5','0','0','7','0','6'],
	['0','B','5','0','0','3','E','1','0','0','0','0','4','A','C','0'],
	['0','E','0','6','G','0','0','A','0','0','D','9','8','0','0','2'],
	['G','0','7','2','0','1','0','0','A','0','0','0','0','0','6','0'],
	['0','C','0','0','0','F','0','0','0','E','2','0','G','0','0','0'],
	['B','A','F','3','E','2','8','0','0','C','1','6','7','0','5','0']
]

# Position of the input elements in the arr
# pos = {
# 	element: [[position 1], [position 2]]
# }
pos = {}

# Count of the remaining number of the elements
# rem = {
# 	element: pending count
# }
rem = {}

# Graph defining tentative positions of the elements to be filled
# graph = {
# 	key: {
# 		row1: [columns],
# 		row2: [columns]
# 	}
# }
graph = {}


# Print the matrix array
def printMatrix():
	for i in range(0, MATRIX_SIZE):
		for j in range(0, MATRIX_SIZE):
			print(str(arr[i][j]), end=" ")
		print()


# Method to check if the inserted element is safe
def is_safe(x, y):
	key = arr[x][y]
	for i in range(0, MATRIX_SIZE):
		if i != y and arr[x][i] == key:
			return False
		if i != x and arr[i][y] == key:
			return False

	r_start = int(x / BLOCK_SIZE) * BLOCK_SIZE
	r_end = r_start + BLOCK_SIZE

	c_start = int(y / BLOCK_SIZE) * BLOCK_SIZE
	c_end = c_start + BLOCK_SIZE

	for i in range(r_start, r_end):
		for j in range(c_start, c_end):
			if i != x and j != y and arr[i][j] == key:
				return False
	return True


# method to fill the matrix
# input keys: list of elements to be filled in the matrix
#		k   : index number of the element to be picked up from keys
#		rows: list of row index where element is to be inserted
#		r   : index number of the row to be inserted
#	
def fill_matrix(k, keys, r, rows):
	for c in graph[keys[k]][rows[r]]:
		if arr[rows[r]][c] != EMPTY_CELL:
			continue
		arr[rows[r]][c] = keys[k]
		if is_safe(rows[r],c):
			if r < len(rows) - 1:
				if fill_matrix(k, keys, r + 1, rows):
					return True
				else:
					arr[rows[r]][c] = EMPTY_CELL
					continue
			else:
				if k < len(keys) - 1:
					if fill_matrix(k + 1, keys, 0, list(graph[keys[k + 1]].keys())):
						return True
					else:
						arr[rows[r]][c] = EMPTY_CELL
						continue
				return True
		arr[rows[r]][c] = EMPTY_CELL
	return False


# Fill the pos and rem dictionary. It will be used to build graph
def build_pos_and_rem():
	for i in range(0, MATRIX_SIZE):
		for j in range(0, MATRIX_SIZE):
			if arr[i][j] != EMPTY_CELL:
				if arr[i][j] not in pos:
					pos[arr[i][j]] = []
				pos[arr[i][j]].append([i,j])
				if arr[i][j] not in rem:
					rem[arr[i][j]] = MATRIX_SIZE
				rem[arr[i][j]] -= 1

	# Fill the elements not present in input matrix. Example: 1 is missing in input matrix
	for i in range(0, MATRIX_SIZE):
		if ELEMENTS[i] not in pos:
			pos[ELEMENTS[i]] = []
		if ELEMENTS[i] not in rem:
			rem[ELEMENTS[i]] = MATRIX_SIZE

# Build the graph
def build_graph():
	for k,v in pos.items():
		if k not in graph:
			graph[k] = {}

		row = list(range(0, MATRIX_SIZE))
		col = list(range(0, MATRIX_SIZE))

		for cord in v:
			row.remove(cord[0])
			col.remove(cord[1])

		if len(row) == 0 or len(col) == 0:
			continue

		for r in row:
			for c in col:
				if arr[r][c] == EMPTY_CELL:
					if r not in graph[k]:
						graph[k][r] = []
					graph[k][r].append(c)


build_pos_and_rem()

# Sort the rem map in order to start with smaller number of elements to be filled first. Optimization for pruning
rem = {k: v for k,v in sorted(rem.items(), key=lambda item: item[1])}

build_graph()

key_s = list(rem.keys())
# Util called to fill the matrix
fill_matrix(0, key_s, 0, list(graph[key_s[0]].keys()))

printMatrix()
