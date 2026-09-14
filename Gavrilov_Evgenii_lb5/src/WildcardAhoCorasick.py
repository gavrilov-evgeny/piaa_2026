#!/usr/bin/env python3

from collections import deque
from typing import List

class TrieNode:
    """Trie node class."""
    def __init__(self) -> None:
        self.isTerminal: bool = False
        self.children: dict[str, TrieNode] = {}
        self.suff: TrieNode | None = None
        self.exit: TrieNode | None = None
        self.patternLen: int | None = None
        self.patternStarts: List[int] = []

class Trie:
    """Trie class"""
    def __init__(self, patterns: List[str] = []) -> None:
        self.root = TrieNode()
        self.patternLen: int = 0
        self.patternCount: int = 0
        if patterns:
            self.buildTrie(patterns)

    def buildTrie(self, patterns: List[str]) -> None:
        """Build trie with Aho-Corasick automaton from a list of patterns"""
        for index, pattern in enumerate(patterns):
            self._add_pattern(pattern, index)
        self._build_automaton()

    def buildFromPattern(self, pattern: str, wildcard: str) -> None:
        """Split a wildcard pattern into fixed parts and build the automaton
        needed to find all full matches of the pattern in a text."""
        parts = pattern.split(wildcard)

        self.patternLen = len(pattern)
        self.patternCount = sum(1 for part in parts if part)

        pos = 0
        for part in parts:
            if part:
                self._add_pattern(part, pos)
            pos += len(part) + len(wildcard)

        self._build_automaton()

    def search(self, text: str) -> List[int]:
        """Search for all occurrences of the wildcard pattern in text using Aho-Corasick."""
        print("\n" + "="*20)
        print("SEARCHING IN TEXT")
        print(f"Text: '{text}'")
        print("="*20)

        match_count = [0] * (len(text) + 1)
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

            # check for matches at current node and along exit links
            node: TrieNode | None = current
            while node is not None and node is not self.root:
                if node.isTerminal:
                    print(f"  MATCH FOUND at node id={id(node)}! patternLen={node.patternLen}, starts={node.patternStarts}")
                    for part_start in node.patternStarts:
                        start = i - node.patternLen - part_start + 2
                        print(f"    Candidate pattern start position: {start}")
                        if 1 <= start <= len(text) - self.patternLen + 1:
                            match_count[start] += 1
                            print(f"    -> counted toward pattern start {start} (count={match_count[start]})")
                node = node.exit
                if node is not None and node is not self.root:
                    print(f"    Following exit link to id={id(node)}")

        print("\nChecking accumulated match counts against required pattern count "
              f"({self.patternCount}):")
        result = []
        for i in range(1, len(text) + 1):
            print(f"  Position {i}: match_count={match_count[i]}")
            if match_count[i] == self.patternCount:
                print(f"    -> Position {i} matches full pattern")
                result.append(i)

        print("="*20 + "\n")

        return result

    def _add_pattern(self, pattern: str, patternStart: int) -> None:
        """Add one pattern to Aho-Corasick trie"""
        print(f"Adding pattern: {pattern}, pattern start: {patternStart}")
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
        current.patternStarts.append(patternStart)

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
            print(f"\nProcessing node id={id(current)} (isTerminal={current.isTerminal}, patternStarts={current.patternStarts})")

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
                desc += f" | TERMINAL (patternStarts={node.patternStarts}, len={node.patternLen})"
            desc += f" | suff: {id(node.suff)}"
            if node.exit is not None:
                desc += f" | exit: {id(node.exit)}"

            print(desc)

            for char, child in node.children.items():
                queue.append((child, path + char, char, id(child)))

        print("="*20 + "\n")

def main():
    text = input()
    pattern = input()
    wildcard = input()

    trie = Trie()
    trie.buildFromPattern(pattern, wildcard)

    results = trie.search(text)
    for position in results:
        print(position)

if __name__ == "__main__":
    main()
