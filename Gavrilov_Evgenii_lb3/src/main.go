package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	var s, t string
	reader := bufio.NewReader(os.Stdin)
	fmt.Fscan(reader, &s)
	fmt.Fscan(reader, &t)

	distance := levenshteinDistance(s, t)
	fmt.Printf("Resulting Levenshtein distance is: %d\n\n\n", distance)
	lengthLCS := longestCommonSubsequence(s, t)
	fmt.Println("Resulting length of longest common subsequence is:", lengthLCS)
}

func printMatrixWithStrings(matrix [][]int, s, t string) {
	fmt.Printf("  %s\n", t)
	for i := range matrix {
		if i >= 1 {
			fmt.Printf("%c", s[i-1])
		} else {
			fmt.Print(" ")
		}
		for j := range matrix[i] {
			fmt.Print(matrix[i][j])
		}
		fmt.Println()
	}
	fmt.Println()
}

func printMatrix(matrix [][]int) {
	for i := range matrix {
		for j := range matrix[i] {
			fmt.Print(matrix[i][j])
		}
		fmt.Println()
	}
	fmt.Println()
}

func levenshteinDistance(s, t string) int {
	m, n := len(s), len(t)
	dp := make([][]int, m+1)
	for i := range dp {
		dp[i] = make([]int, n+1)
	}

	fmt.Printf("\tCalculating Levenshtein distance between the strings %s and %s\n", s, t)
	for i := 0; i <= m; i++ {
		dp[i][0] = i
	}
	for j := 0; j <= n; j++ {
		dp[0][j] = j
	}
	fmt.Println("Initial matrix of operations:")
	printMatrixWithStrings(dp, s, t)

	fmt.Printf("Starting calculations\n\n")
	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			fmt.Printf("Now on position (%d, %d)\n", i, j)
			fmt.Printf("In the strings, position maps to symbols: %c, %c\n", s[i-1], t[j-1])
			if s[i-1] == t[j-1] {
				dp[i][j] = dp[i-1][j-1]
				fmt.Println("Symbols match! The resulting value for the position is ", dp[i][j])
				fmt.Println("\tTook action MATCH")
				fmt.Println("Now matrix looks like:")
				printMatrix(dp)
			} else {
				dp[i][j] = min(
					dp[i-1][j]+1,
					dp[i][j-1]+1,
					dp[i-1][j-1]+1,
				)
				fmt.Println("Symbols don't match! The resulting value for the position is ", dp[i][j])
				if dp[i][j] == dp[i-1][j]+1 {
					fmt.Println("\tTook action DELETE (or other action, if listed)")
				}
				if dp[i][j] == dp[i-1][j-1]+1 {
					fmt.Println("\tTook action REPLACE (or other action, if listed)")
				}
				if dp[i][j] == dp[i][j-1]+1 {
					fmt.Println("\tTook action INSERT (or other action, if listed)")
				}
				fmt.Println("Now matrix looks like:")
				printMatrix(dp)
			}
		}
	}

	return dp[m][n]
}

func longestCommonSubsequence(s, t string) int {
	m, n := len(s), len(t)

	dp := make([][]int, m+1)
	for i := range dp {
		dp[i] = make([]int, n+1)
	}

	fmt.Printf("\tCalculating length of LCS of the strings %s and %s\n", s, t)

	for i := 1; i <= m; i++ {
		for j := 1; j <= n; j++ {
			fmt.Printf("Now on position (%d, %d)\n", i, j)
			fmt.Printf("In the strings, position maps to symbols: %c, %c\n", s[i-1], t[j-1])
			if s[i-1] == t[j-1] {
				dp[i][j] = dp[i-1][j-1] + 1
				fmt.Println("Symbols match! The resulting length of LCS for the prefix is ", dp[i][j])
			} else {
				dp[i][j] = max(dp[i-1][j], dp[i][j-1])
				fmt.Println("Symbols don't! The resulting length of LCS for the prefix is ", dp[i][j])
			}
			fmt.Println("Now matrix looks like:")
			printMatrix(dp)
		}
	}

	return dp[m][n]
}
