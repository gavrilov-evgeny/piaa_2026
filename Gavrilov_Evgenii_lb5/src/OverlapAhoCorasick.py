#!/usr/bin/env python3

from collections import deque
from typing import List, Tuple

class TrieNode:
    """Trie node class."""
    def __init__(self) -> None:
        self.isTerminal: bool = False
        self.children: dict[str, TrieNode] = {}
        self.suff: TrieNode | None = None
        self.exit: TrieNode | None = None
        self.patternLen: int | None = None
        self.patternIndex: int | None = None

class Trie:
    """Trie class"""
    def __init__(self, patterns: List[str] = []) -> None:
        self.root = TrieNode()
        self.patternLens: dict[int, int] = {}
        if patterns:
            self.buildTrie(patterns)

    def buildTrie(self, patterns: List[str]) -> None:
        """Build trie with Aho-Corasick automaton from a list of patterns"""
        for index, pattern in enumerate(patterns):
            self._add_pattern(pattern, index)
        self._build_automaton()

    def countNodes(self) -> int:
        """Count the total number of vertices (nodes) in the automaton."""
        print("\n" + "="*20)
        print("COUNTING AUTOMATON VERTICES")
        print("="*20)

        count = 0
        queue = deque([self.root])

        while queue:
            node = queue.popleft()
            count += 1
            print(f"  Counting node id={id(node)} (total so far: {count})")

            for char, child in node.children.items():
                queue.append(child)

        print(f"Total number of vertices: {count}")
        print("="*20 + "\n")

        return count

    def findOverlappingMatches(self, matches: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        print("\n" + "="*20)
        print("CHECKING FOUND PATTERNS FOR INTERSECTIONS")
        print(f"Found matches: {matches}")
        print("="*20)

        overlapping: List[Tuple[int, int]] = []

        for idx, (pos, patternIndex) in enumerate(matches):
            patternLen = self.patternLens[patternIndex - 1]
            start = pos
            end = pos + patternLen - 1
            print(f"\n  Checking pattern {patternIndex} at position {pos} (occupies [{start}, {end}])")

            has_overlap = False
            for other_idx, (other_pos, other_patternIndex) in enumerate(matches):
                if other_idx == idx:
                    continue
                other_len = self.patternLens[other_patternIndex - 1]
                other_start = other_pos
                other_end = other_pos + other_len - 1

                if start <= other_end and other_start <= end:
                    print(f"    Overlaps with pattern {other_patternIndex} at position {other_pos} "
                          f"(occupies [{other_start}, {other_end}])")
                    has_overlap = True

            if has_overlap:
                print(f"  -> Pattern {patternIndex} at position {pos} has at least one intersection")
                overlapping.append((pos, patternIndex))
            else:
                print(f"  -> Pattern {patternIndex} at position {pos} has no intersections")

        print(f"\nMatches with intersections: {overlapping}")
        print("="*20 + "\n")

        return overlapping

    def search(self, text: str) -> List[Tuple[int, int]]:
        """Search for all occurrences of patterns in text using Aho-Corasick."""
        print("\n" + "="*20)
        print("SEARCHING IN TEXT")
        print(f"Text: '{text}'")
        print("="*20)

        result = []
        current: TrieNode = self.root

        print(f"\nInitial state: current = ROOT (id={id(self.root)})")

        for i, char in enumerate(text):
            print(f"\n--- Processing character '{char}' at position {i} ---")
            print(f"  Current node before transition: id={id(current)} (isTerminal={current.isTerminal})")

            # follow failure links until we find a match or reach root
            while current is not self.root and char not in current.children:
                print(f"  Char '{char}' not in current's children, following suff link from id={id(current)}")
                current = current.suff
                print(f"  New current: id={id(current)} (isTerminal={current.isTerminal})")

            # next state
            if char in current.children:
                current = current.children[char]
                print(f"  Char '{char}' found in children, moving to id={id(current)}")
            else:
                current = self.root
                print(f"  Char '{char}' not found, staying at ROOT (id={id(self.root)})")

            # check for matches at current node
            if current.isTerminal:
                start_pos = i - current.patternLen + 2
                print(f"  MATCH FOUND at current node! patternIndex={current.patternIndex}, patternLen={current.patternLen}")
                print(f"    Start position: {start_pos}, Pattern index: {current.patternIndex + 1}")
                result.append((start_pos, current.patternIndex + 1))

            # check exit links
            temp = current.exit
            if temp is not None:
                print(f"  Checking exit links from id={id(current)}")
            while temp is not None:
                start_pos = i - temp.patternLen + 2
                print(f"  EXIT LINK MATCH! patternIndex={temp.patternIndex}, patternLen={temp.patternLen}")
                print(f"    Start position: {start_pos}, Pattern index: {temp.patternIndex + 1}")
                result.append((start_pos, temp.patternIndex + 1))
                temp = temp.exit
                if temp is not None:
                    print(f"    Following next exit link to id={id(temp)}")

        print("="*20 + "\n")

        return result

    def _add_pattern(self, pattern: str, patternIndex: int) -> None:
        """Add one pattern to Aho-Corasick trie"""
        print(f"Adding pattern: {pattern}, pattern index: {patternIndex}")
        print(f"\nTrie before adding {pattern}:")
        self._print_trie()

        current = self.root
        for char in pattern:
            print(f"Adding char: {char} from the pattern that we are adding")
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.isTerminal = True
        current.patternLen = len(pattern)
        current.patternIndex = patternIndex
        self.patternLens[patternIndex] = len(pattern)

        print(f"\nTrie after adding {pattern}:")
        self._print_trie()

    def _build_automaton(self) -> None:
        """Build the Aho-Corasick automaton by setting up failure links (suff)
        and dictionary links (exit) for all nodes."""
        queue = deque()
        print("BUILDING AUTOMATON")
        print("\nTrie before building automaton:")
        self._print_trie()

        for char, child in self.root.children.items():
            # root suff is root
            print(f"Setting suff link for root's child '{char}' (id={id(child)}) to ROOT (id={id(self.root)})")
            child.suff = self.root
            queue.append(child)

        while queue:
            current = queue.popleft()
            print(f"\nProcessing node id={id(current)} (isTerminal={current.isTerminal}, patternIndex={current.patternIndex})")

            for char, child in current.children.items():
                print(f"  Processing child '{char}' (id={id(child)}) of node id={id(current)}")

                # start from current suff
                fallback = current.suff
                print(f"    Starting fallback from suff link: id={id(fallback) if fallback else None}")

                # follow suff until we find char as child or reach root
                while fallback is not None and char not in fallback.children:
                    print(f"    Char '{char}' not in fallback's children, following suff link from id={id(fallback)}")
                    fallback = fallback.suff
                    print(f"    New fallback: id={id(fallback) if fallback else None}")

                # set suff
                if fallback is None:
                    child.suff = self.root
                    print(f"    Fallback is None, setting suff link to ROOT (id={id(self.root)})")
                else:
                    child.suff = fallback.children[char]
                    print(f"    Setting suff link to id={id(child.suff)}")

                # set exit link
                if child.suff.isTerminal:
                    child.exit = child.suff
                    print(f"    Suff link node is TERMINAL, setting exit link to id={id(child.exit)}")
                else:
                    child.exit = child.suff.exit
                    if child.exit is not None:
                        print(f"    Inheriting exit link from suff link: id={id(child.exit)}")
                    else:
                        print(f"    No exit link to inherit (None)")

                queue.append(child)
                print(f"    Added child '{char}' (id={id(child)}) to queue")

        print("\nTrie after building automaton")
        self._print_trie()

    def _print_trie(self) -> None:
        print("="*20)
        print("\tTrie nodes (BFS):")

        queue = deque([(self.root, "", "ROOT", id(self.root))])

        while queue:
            node, path, label, wid = queue.popleft()

            desc = f"  {wid}: '{label}' | path='{path}'"
            if node.isTerminal:
                desc += f" | TERMINAL (patternIndex={node.patternIndex}, len={node.patternLen})"
            desc += f" | suff: {id(node.suff)}"
            if node.exit is not None:
                desc += f" | exit: {id(node.exit)}"

            print(desc)

            for char, child in node.children.items():
                queue.append((child, path + char, char, id(child)))

        print("="*20 + "\n")

def main():
    text = input()
    n = int(input())
    patterns = [input() for _ in range(n)]
    trie = Trie(patterns)

    node_count = trie.countNodes()
    print(f"Number of automaton vertices: {node_count}")

    results = trie.search(text)
    results.sort(key=lambda x: (x[0], x[1]))
    for position, index in results:
        print(position, index)

    overlapping = trie.findOverlappingMatches(results)
    overlapping.sort(key=lambda x: (x[0], x[1]))
    print("Found patterns intersecting with other found patterns:")
    for position, index in overlapping:
        print(position, index)

if __name__ == "__main__":
    main()
