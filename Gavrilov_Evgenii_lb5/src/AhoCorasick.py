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
        self.wordLen: int | None = None
        self.wordIndex: int | None = None

class Trie:
    """Trie class"""
    def __init__(self, words: List[str] = []) -> None:
        self.root = TrieNode()
        if words:
            self.buildTrie(words)

    def buildTrie(self, words: List[str]) -> None:
        """Build trie with Aho-Corasick automaton from a list of words"""
        for index, word in enumerate(words):
            self._add_word(word, index)
        self._build_automaton()

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
                start_pos = i - current.wordLen + 2
                print(f"  MATCH FOUND at current node! wordIndex={current.wordIndex}, wordLen={current.wordLen}")
                print(f"    Start position: {start_pos}, Pattern index: {current.wordIndex + 1}")
                result.append((start_pos, current.wordIndex + 1))

            # check exit links
            temp = current.exit
            if temp is not None:
                print(f"  Checking exit links from id={id(current)}")
            while temp is not None:
                start_pos = i - temp.wordLen + 2
                print(f"  EXIT LINK MATCH! wordIndex={temp.wordIndex}, wordLen={temp.wordLen}")
                print(f"    Start position: {start_pos}, Pattern index: {temp.wordIndex + 1}")
                result.append((start_pos, temp.wordIndex + 1))
                temp = temp.exit
                if temp is not None:
                    print(f"    Following next exit link to id={id(temp)}")

        print("="*20 + "\n")

        return result

    def _add_word(self, word: str, wordIndex: int) -> None:
        """Add one word to Aho-Corasick trie"""
        print(f"Adding word: {word}, word index: {wordIndex}")
        print(f"\nTrie before adding {word}:")
        self._print_trie()

        current = self.root
        for char in word:
            print(f"Adding char: {char} from the word that we are adding")
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.isTerminal = True
        current.wordLen = len(word)
        current.wordIndex = wordIndex

        print(f"\nTrie after adding {word}:")
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
            print(f"\nProcessing node id={id(current)} (isTerminal={current.isTerminal}, wordIndex={current.wordIndex})")

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
                desc += f" | TERMINAL (wordIndex={node.wordIndex}, len={node.wordLen})"
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
    words = [input() for _ in range(n)]
    trie = Trie(words)
    results = trie.search(text)
    results.sort(key=lambda x: (x[0], x[1]))
    for position, index in results:
        print(position, index)

if __name__ == "__main__":
    main()