#!/usr/bin/env python3

import random
import sys


class Graph:
    def __init__(self, matrix):
        self.matrix = matrix
        self.size = len(matrix)

    def get_dist(self, u, v):
        dist = self.matrix[u][v]
        return dist if dist > 0 or u == v else float("inf")


class Alsh2:
    def __init__(self, graph, debug=False):
        self.graph = graph
        self.debug = debug

    def _log(self, message):
        if self.debug:
            print(message)

    def solve(self):
        n = self.graph.size
        path = [0, 0] # initial path
        unvisited = list(range(1, n))
        cost = 0 # 0 -> 0 takes 0 cost

        self._log("\n" + "=" * 20)
        self._log("ALSH-2 ALGORITHM")
        self._log(f"Number of cities: {n}")
        self._log(f"Initial path: {path}")
        self._log("=" * 20)

        while unvisited: # while there are cities to visit
            best = None # we want to find best city and its insertion position
            self._log(f"\nCurrent path: {path}")
            self._log(f"Unvisited cities: {unvisited}")

            for city in unvisited: # for each city not in path
                # find the smallest distance from the city to the current path
                nearest = min(
                    self.graph.get_dist(current, city)
                    for current in path[:-1]
                )

                # try to insert the city between each pair of neighbours
                for position in range(len(path) - 1):
                    left = path[position]
                    right = path[position + 1]
                    left_dist = self.graph.get_dist(left, city)
                    right_dist = self.graph.get_dist(city, right)

                    # both new edges must exist
                    if left_dist == float("inf") or right_dist == float("inf"):
                        continue

                    # calculate the increase in the path cost
                    increase = (
                        left_dist
                        + right_dist
                        - self.graph.get_dist(left, right)
                    )
                    candidate = (nearest, increase, city, position)

                    self._log(
                        f"\tTry city {city} between {left} and {right}: "
                        f"nearest={nearest}, increase={increase}"
                    )

                    if best is None or candidate < best: # store the best insertion
                        best = candidate

            # no remaining city can be inserted into the current path
            if best is None:
                self._log("THERE IS NO PATH!")
                self._log("=" * 20 + "\n")
                return "no path", None

            _, increase, city, position = best
            path.insert(position + 1, city) # insert the nearest city
            unvisited.remove(city) # mark the city as visited
            cost += increase # update the path cost

            self._log(
                f"\tINSERT city {city} at position {position + 1}: "
                f"increase={increase}"
            )

        self._log(f"\nApproximate cost: {cost}")
        self._log(f"Approximate path: {' -> '.join(map(str, path))}")
        self._log("=" * 20 + "\n")
        return cost, path


class HeldKarp:
    def __init__(self, graph, debug=False):
        self.graph = graph
        self.debug = debug

    def _log(self, message):
        if self.debug:
            print(message)

    def _mask(self, mask):
        return format(mask, f"0{self.graph.size}b")

    def _visited(self, mask):
        return [city for city in range(self.graph.size) if mask & (1 << city)]

    def _print_memo(self, memo):
        if not self.debug:
            return

        n = self.graph.size
        self._log("=" * 20)
        self._log("\tDP table")
        self._log("mask\t" + "\t".join(f"u={u}" for u in range(n)))

        for mask, row in enumerate(memo):
            if (mask & 1):
                values = ["inf" if value == float("inf") else str(value) for value in row]
                self._log(
                    f"{self._mask(mask)}\t" + "\t".join(values)
                )

        self._log("=" * 20)

    def solve(self):
        n = self.graph.size
        full_mask = (1 << n) - 1 # mask: all cities are visited
        memo = [[float("inf")] * n for _ in range(1 << n)] # all distances are unknown
        parent = [[-1] * n for _ in range(1 << n)] # we don't what paths are

        self._log("\n" + "=" * 20)
        self._log("HELD-KARP ALGORITHM")
        self._log(f"Number of cities: {n}")
        self._log(f"Full mask: {self._mask(full_mask)}")
        self._log("=" * 20)
        self._log("\nDistance matrix:")

        for row in self.graph.matrix:
            self._log("\t" + "\t".join(map(str, row)))

        self._log("\n\tInitializing base states")
        for u in range(n): # for each city
            # if all cities are visited, we only should come back to start
            memo[full_mask][u] = self.graph.get_dist(u, 0)
            self._log(
                f"\tmemo[{self._mask(full_mask)}][{u}] = "
                f"distance({u}, 0) = {memo[full_mask][u]}"
            )

        self._log("\nMemo after initialization:")
        self._print_memo(memo)

        self._log("\n\tFilling DP table")
        for mask in range(full_mask - 1, 0, -1):
            # if 0-city (mask 00...001) isn't visited, it's not a valid path
            # (all paths start from a 0-city)
            if not (mask & 1):
                continue

            self._log(
                f"\nProcessing mask {self._mask(mask)}, "
                f"visited cities: {self._visited(mask)}"
            )

            for u in range(n): # for each current city
                # if current city isn't visited, it's not a valid path
                # (how did we get here?..)
                if not (mask & (1 << u)):
                    continue

                self._log(f"\tCurrent city: {u}")
                for v in range(n): # for each city to which we want to travel
                    # it's no use to visit cities we already have visited
                    # we visit each city only once
                    if mask & (1 << v):
                        continue

                    # calculate the distance
                    dist = self.graph.get_dist(u, v)
                    # calculate overall distance of travelling
                    # (using overall distance of path from v to the finish)
                    next_mask = mask | (1 << v)
                    remaining = memo[next_mask][v]
                    new_dist = dist + remaining

                    self._log(
                        f"\t\t{u} -> {v}: dist={dist}, "
                        f"next mask={self._mask(next_mask)}, "
                        f"remaining={remaining}, new_dist={new_dist}"
                    )

                    if new_dist < memo[mask][u]: # if it's optimal, store it to memo
                        memo[mask][u] = new_dist
                        parent[mask][u] = v # (mask, u) -> v is optimal

                        self._log(
                            f"\t\t\tUPDATE: memo[{self._mask(mask)}][{u}] "
                            f"= {new_dist}, parent = {v}"
                        )

                self._log(
                    f"\tBest state value: memo[{self._mask(mask)}][{u}] "
                    f"= {memo[mask][u]}"
                )

        self._log("\nMemo after filling:")
        self._print_memo(memo)

        min_cost = memo[1][0] # we're in 0-city, and it's visited

        self._log("\n\tDynamic programming completed")
        self._log(f"Initial state: mask={self._mask(1)}, city=0")
        self._log(f"Minimum cost: {min_cost}")

        if min_cost == float("inf"):
            self._log("THERE IS NO PATH!")
            self._log("=" * 20 + "\n")

            return "no path", None

        # restoring the actual path
        self._log("\n\tRestoring the path")
        path = [0]
        mask = 1
        city = 0
        while mask != full_mask: # while we've not visited all the cities
            next_city = parent[mask][city] # how did we get here?
            next_mask = mask | (1 << next_city)

            self._log(
                f"\tmask={self._mask(mask)}, city={city}, "
                f"parent={next_city} -> new mask={self._mask(next_mask)}"
            )

            city = next_city
            path.append(city) # store it
            mask = next_mask # we've visited this city
        path.append(0) # come back to start

        self._log("Return to city 0")
        self._log(f"Optimal path: {' -> '.join(map(str, path))}")
        self._log("=" * 20 + "\n")
        return min_cost, path


def generate_matrix(size, symmetric=False, min_weight=1, max_weight=100):
    matrix = [[0] * size for _ in range(size)]

    if symmetric:
        for row in range(size):
            for column in range(row + 1, size):
                weight = random.randint(min_weight, max_weight)
                matrix[row][column] = weight
                matrix[column][row] = weight
    else:
        for row in range(size):
            for column in range(size):
                if row != column:
                    matrix[row][column] = random.randint(
                        min_weight, max_weight
                    )

    return matrix


def save_graph(graph: Graph, filename):
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(f"{graph.size}\n")
        for row in graph.matrix:
            output_file.write(" ".join(map(str, row)) + "\n")


def load_graph(filename):
    with open(filename, "r", encoding="utf-8") as input_file:
        size = int(input_file.readline())
        matrix = [
            list(map(int, input_file.readline().split()))
            for _ in range(size)
        ]
    return Graph(matrix)


def main():
    n = int(input())
    matrix = [list(map(int, input().split())) for _ in range(n)]
    # matrix = generate_matrix(10)
    graph = Graph(matrix)
    # save_graph(graph, "graph.txt")
    # graph = load_graph("graph.txt")
    debug = "--debug" in sys.argv[1:]

    #solver = Alsh2
    solver = HeldKarp
    cost, path = solver(graph, debug).solve()

    if path is None:
        print("no path")
    else:
        print(cost)
        print(*path)


if __name__ == "__main__":
    main()
