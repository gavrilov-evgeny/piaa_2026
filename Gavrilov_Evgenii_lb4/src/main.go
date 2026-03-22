package main

import (
	"bufio"
	"fmt"
	"os"
)

func computePrefixFunction(pattern string) []int {
	fmt.Printf("Computing prefix function for pattern: %s\n", pattern)
	patternLength := len(pattern)
	prefix := make([]int, patternLength)
	i := 1
	j := 0
	for i < patternLength {
		fmt.Printf("Current state: i=%d, j=%d; pattern[i]=%c, pattern[j]=%c\n", i, j, pattern[i], pattern[j])
		if pattern[i] == pattern[j] {
			prefix[i] = j + 1
			fmt.Printf("Symbols match; prefix[i]=%d; i and j shifted right\n", prefix[i])
			i++
			j++
		} else {
			if j == 0 {
				fmt.Println("Symbols do not match; prefix is in the beginning; i shifted right")
				i++
			} else {
				fmt.Println("Symbols do not match; j shifted to prefix[j-1]")
				j = prefix[j-1]
			}
		}
	}
	fmt.Printf("Final prefix array for pattern %s: %v\n\n", pattern, prefix)
	return prefix
}

func kmp(pattern, text string) []int {
	patternIndex := 0
	textIndex := 0
	patternLength := len(pattern)
	textLength := len(text)

	var matches []int
	prefix := computePrefixFunction(pattern)
	fmt.Printf("Searching for pattern '%s' in text '%s' using KMP algorithm\n", pattern, text)
	for textIndex < textLength {
		fmt.Printf("\tNow on textIndex=%d, patternIndex=%d\n", textIndex, patternIndex)
		fmt.Printf("Current symbols: on text '%c', pattern '%c'\n", text[textIndex], pattern[patternIndex])
		if pattern[patternIndex] == text[textIndex] {
			fmt.Println("Symbols match; shift right on both strings")
			patternIndex++
			textIndex++
			if patternIndex == patternLength {
				matches = append(matches, textIndex-patternIndex)
				fmt.Printf("What's more, full substring match is found! Index added to matches: %v\n", matches)
				patternIndex = prefix[patternIndex-1]
				fmt.Printf("patternIndex shifted left to the position of last prefix function: %d\n", patternIndex)
			}
		} else {
			fmt.Print("Symbols do not match; ")
			if patternIndex == 0 {
				fmt.Println("we're on the beginning of the pattern, so shift right on a text string")
				textIndex++
			} else {
				fmt.Println("we're not on the beginning of the pattern, so we change")
				fmt.Println("pattern position to the position pointed by last prefix function")
				patternIndex = prefix[patternIndex-1]
			}
		}
	}
	fmt.Println("\tReached end of text")
	fmt.Printf("Final array consisting of starting indices in text where pattern occurs: %v\n\n", matches)
	return matches
}

func solveKmp() {
	var pattern, text string
	reader := bufio.NewReader(os.Stdin)
	fmt.Fscan(reader, &pattern)
	fmt.Fscan(reader, &text)
	matches := kmp(pattern, text)
	if len(matches) > 0 {
		for i, match := range matches {
			if i > 0 {
				fmt.Print(",")
			}
			fmt.Print(match)
		}
		fmt.Println()
	} else {
		fmt.Println("Matches not found")
		fmt.Println("-1")
	}
}

func solveCyclicShift() {
	var pattern, text string
	reader := bufio.NewReader(os.Stdin)
	fmt.Fscan(reader, &text)
	fmt.Fscan(reader, &pattern)
	if len(pattern) != len(text) {
		fmt.Println("Pattern and text's lengths are not equal")
		fmt.Println("-1")
	} else {
		matches := kmp(pattern, text+text)
		if len(matches) > 0 {
			fmt.Println(matches[0])
		} else {
			fmt.Println("Matches not found")
			fmt.Println("-1")
		}
	}
}

func main() {
	solveKmp()
	solveCyclicShift()
}
