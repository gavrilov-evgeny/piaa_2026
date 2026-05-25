package main

import (
	"fmt"
)

// Square represents a placed square on the board
type Square struct {
	x, y, size int
}

// State represents a single frame in the backtracking stack
type State struct {
	currentSquares []Square
	count          int
	row            int
	col            int
	sizeIndex      int   // current index in the sizes list we're trying
	sizes          []int // list of sizes to try at this position
	board          []int // copy of board state at this frame
}

// Solver encapsulates the state for solving the square packing problem
type Solver struct {
	boardSize   int
	bestCount   int
	bestSquares []Square
	board       []int // bitmask representation of occupied cells
}

// NewSolver creates a new Solver instance for a given board size
func NewSolver(n int) *Solver {
	return &Solver{
		boardSize: n,
	}
}

// place adds or removes a square from the board using bitmask operations
func (s *Solver) place(row, col, size int, add bool) {
	if add {
		fmt.Printf("\nPlacing a square of size %d to position (%d, %d)\n", size, row, col)
	} else {
		fmt.Printf("\nRemoving a square of size %d from position (%d, %d)\n", size, row, col)
	}

	mask := ((1 << size) - 1) << col
	for i := row; i < row+size; i++ {
		if add {
			s.board[i] |= mask
		} else {
			s.board[i] &^= mask
		}
	}

	fmt.Println("Resulting board:")
	s.printBoard()
}

// findEmpty locates the topmost-leftmost empty cell
func (s *Solver) findEmpty() (int, int) {
	fmt.Println("Finding topmost-leftmost empty cell...")

	fullMask := (1 << s.boardSize) - 1
	for row := 0; row < s.boardSize; row++ {
		if s.board[row] != fullMask {
			col := 0
			for (s.board[row]>>col)&1 == 1 {
				col++
			}
			fmt.Printf("Empty cell found on position (%d, %d)\n", row, col)
			return row, col
		}
	}
	fmt.Println("Empty cell not found")
	return -1, -1
}

// maxSquareSize determines the largest square that can fit at (row, col)
func (s *Solver) maxSquareSize(row, col int) int {
	fmt.Printf("\nFinding the largest square that can fit at (%d, %d)\n", row, col)

	maxSize := s.boardSize - row
	if s.boardSize-col < maxSize {
		maxSize = s.boardSize - col
	}

	for size := 1; size <= maxSize; size++ {
		mask := ((1 << size) - 1) << col
		for i := row; i < row+size; i++ {
			if s.board[i]&mask != 0 {
				fmt.Printf("Largest square at (%d, %d) has size %d\n", row, col, size-1)
				return size - 1
			}
		}
	}
	fmt.Printf("The largest square on (%d, %d) is of size %d\n", row, col, maxSize)
	return maxSize
}

// copyBoard creates a deep copy of the current board
func (s *Solver) copyBoard() []int {
	newBoard := make([]int, s.boardSize)
	copy(newBoard, s.board)
	return newBoard
}

// restoreBoard restores the board from a saved state
func (s *Solver) restoreBoard(savedBoard []int) {
	copy(s.board, savedBoard)
}

// backtrack performs iterative search for optimal square packing using a stack
func (s *Solver) backtrack(initialSquares []Square, initialCount int) {
	// Stack of states to process
	stack := []State{}

	// Initial state setup
	row, col := s.findEmpty()
	sizes := []int{}
	if row != -1 {
		maxSize := s.maxSquareSize(row, col)
		sizes = make([]int, maxSize)
		for i := 0; i < maxSize; i++ {
			sizes[i] = maxSize - i // descending order
		}
	}

	initialState := State{
		currentSquares: make([]Square, len(initialSquares)),
		count:          initialCount,
		row:            row,
		col:            col,
		sizeIndex:      0,
		sizes:          sizes,
		board:          s.copyBoard(),
	}
	copy(initialState.currentSquares, initialSquares)

	stack = append(stack, initialState)

	fmt.Println("\nBACKTRACK CALL")
	fmt.Printf("Current depth: %d\n", initialCount)
	fmt.Printf("Current squares count: %d\n", len(initialSquares))
	fmt.Print("Current squares: [")
	for i, sq := range initialSquares {
		if i > 0 {
			fmt.Print(", ")
		}
		fmt.Printf("(%d,%d,%d)", sq.x, sq.y, sq.size)
	}
	fmt.Println("]")
	fmt.Printf("Best count so far: %d\n", s.bestCount)

	for len(stack) > 0 {
		// Peek at the top state
		current := &stack[len(stack)-1]

		// Check if board is completely filled
		if current.row == -1 {
			fmt.Println("\n\tBOARD COMPLETELY FILLED!!!")
			fmt.Printf("Solution found with %d squares\n", current.count)
			if current.count < s.bestCount {
				fmt.Printf("NEW BEST SOLUTION! Previous best: %d -> New best: %d\n", s.bestCount, current.count)
				s.bestCount = current.count
				s.bestSquares = make([]Square, current.count)
				copy(s.bestSquares, current.currentSquares)
			} else {
				fmt.Printf("Solution is not better than current best: %d\n", s.bestCount)
			}
			// Pop this state
			stack = stack[:len(stack)-1]
			if len(stack) > 0 {
				// Restore board from the parent state
				s.restoreBoard(stack[len(stack)-1].board)
			}
			if len(stack) > 0 {
				fmt.Printf("BACKTRACK RETURN (depth %d)\n", stack[len(stack)-1].count)
			}
			continue
		}

		// Pruning: no need to continue if we already have a better solution
		if current.count+1 >= s.bestCount {
			fmt.Printf("PRUNING: count+1 (%d) >= bestCount (%d) - abandoning this branch\n", current.count+1, s.bestCount)
			// Pop this state
			stack = stack[:len(stack)-1]
			if len(stack) > 0 {
				s.restoreBoard(stack[len(stack)-1].board)
			}
			if len(stack) > 0 {
				fmt.Printf("BACKTRACK RETURN (depth %d)\n", stack[len(stack)-1].count)
			}
			continue
		}

		// If we've tried all sizes for this position, pop the state
		if current.sizeIndex >= len(current.sizes) {
			stack = stack[:len(stack)-1]
			if len(stack) > 0 {
				s.restoreBoard(stack[len(stack)-1].board)
			}
			if len(stack) > 0 {
				fmt.Printf("BACKTRACK RETURN (depth %d)\n", stack[len(stack)-1].count)
			}
			continue
		}

		// This is where we need to simulate the recursive call structure
		// Print the backtrack call header for each new position we're exploring
		if current.sizeIndex == 0 {
			fmt.Println("\nBACKTRACK CALL")
			fmt.Printf("Current depth: %d\n", current.count)
			fmt.Printf("Current squares count: %d\n", len(current.currentSquares))
			fmt.Print("Current squares: [")
			for i, sq := range current.currentSquares {
				if i > 0 {
					fmt.Print(", ")
				}
				fmt.Printf("(%d,%d,%d)", sq.x, sq.y, sq.size)
			}
			fmt.Println("]")
			fmt.Printf("Best count so far: %d\n", s.bestCount)
		}

		// Get the current size to try
		size := current.sizes[current.sizeIndex]
		current.sizeIndex++

		fmt.Printf("\n--- Trying size %d at position (%d, %d) ---\n", size, current.row, current.col)

		// Save current board before placing
		savedBoard := s.copyBoard()
		s.restoreBoard(current.board)

		// Place the square
		s.place(current.row, current.col, size, true)

		// Find next empty cell for the recursive call
		nextRow, nextCol := s.findEmpty()
		nextSizes := []int{}
		if nextRow != -1 {
			nextMaxSize := s.maxSquareSize(nextRow, nextCol)
			nextSizes = make([]int, nextMaxSize)
			for i := 0; i < nextMaxSize; i++ {
				nextSizes[i] = nextMaxSize - i
			}
		}

		// Create new squares list
		newSquares := make([]Square, len(current.currentSquares)+1)
		copy(newSquares, current.currentSquares)
		newSquares[len(current.currentSquares)] = Square{
			x:    current.row + 1,
			y:    current.col + 1,
			size: size,
		}

		// Push new state onto stack (this represents the recursive call)
		newState := State{
			currentSquares: newSquares,
			count:          current.count + 1,
			row:            nextRow,
			col:            nextCol,
			sizeIndex:      0,
			sizes:          nextSizes,
			board:          s.copyBoard(),
		}
		stack = append(stack, newState)

		// Restore the board for the current state (it will be restored again when we come back)
		s.restoreBoard(savedBoard)
	}
}

// solveEven handles even-sized boards with optimal solution (4 squares)
func (s *Solver) solveEven() (int, []Square) {
	half := s.boardSize / 2
	return 4, []Square{
		{1, 1, half},
		{1, half + 1, half},
		{half + 1, 1, half},
		{half + 1, half + 1, half},
	}
}

// scaleSolution scales a solution for composite board sizes
func scaleSolution(count int, squares []Square, factor int) (int, []Square) {
	scaled := make([]Square, count)
	for i, sq := range squares {
		scaled[i] = Square{
			x:    (sq.x-1)*factor + 1,
			y:    (sq.y-1)*factor + 1,
			size: sq.size * factor,
		}
	}
	return count, scaled
}

// solve finds the optimal square packing for the current board size
func (s *Solver) solve() (int, []Square) {
	fmt.Printf("Finding optimal solution for square size: %d\n", s.boardSize)
	// Even-sized boards have a known optimal solution
	if s.boardSize%2 == 0 {
		fmt.Println("N is even, so solution is trivial:\n")
		return s.solveEven()
	}

	// For composite sizes, solve for the smallest prime factor and scale up
	prime := smallestPrimeFactor(s.boardSize)
	if prime < s.boardSize {
		fmt.Println("N is composite number, so we solve for the size of the smallest")
		fmt.Printf("prime factor (%d), then scale the found solution up\n", prime)
		// Create a sub-solver for the prime-sized board
		subSolver := NewSolver(prime)
		count, squares := subSolver.solve()
		return scaleSolution(count, squares, s.boardSize/prime)
	}

	fmt.Printf("Board size %d is prime - performing full search\n", s.boardSize)

	// Initialize search for prime sizes
	s.bestCount = s.boardSize * s.boardSize
	s.bestSquares = nil
	s.board = make([]int, s.boardSize)

	// Place three initial squares for optimization
	if s.boardSize > 2 {
		size1 := (s.boardSize + 1) / 2
		size2 := (s.boardSize - 1) / 2

		s.place(0, 0, size1, true)
		s.place(0, size1, size2, true)
		s.place(size1, 0, size2, true)

		initialSquares := []Square{
			{1, 1, size1},
			{1, size1 + 1, size2},
			{size1 + 1, 1, size2},
		}

		fmt.Println("Heuristic initial placement:")
		fmt.Printf("  Square 1: size %d at position (0,0)\n", size1)
		fmt.Printf("  Square 2: size %d at position (0,%d)\n", size2, size1)
		fmt.Printf("  Square 3: size %d at position (%d,0)\n", size2, size1)

		s.backtrack(initialSquares, len(initialSquares))
	} else {
		s.backtrack([]Square{}, 0)
	}

	return s.bestCount, s.bestSquares
}

func smallestPrimeFactor(n int) int {
	for i := 2; i*i <= n; i++ {
		if n%i == 0 {
			fmt.Printf("Found smallest prime factor for number %d it's %d\n", n, i)
			return i
		}
	}
	fmt.Printf("Found smallest prime factor for number %d it's %d\n", n, n)
	return n
}

func (s *Solver) printBoard() {
	if len(s.board) == 0 {
		fmt.Println("Board isn't initialised")
		return
	}

	for row := 0; row < s.boardSize; row++ {
		for col := 0; col < s.boardSize; col++ {
			if (s.board[row]>>col)&1 == 1 {
				fmt.Print("■ ")
			} else {
				fmt.Print("□ ")
			}
		}
		fmt.Println()
	}
	fmt.Println()
}

func main() {
	var boardSize int
	fmt.Scan(&boardSize)

	solver := NewSolver(boardSize)
	count, squares := solver.solve()

	fmt.Println(count)
	for _, sq := range squares {
		fmt.Printf("%d %d %d\n", sq.x, sq.y, sq.size)
	}
}
