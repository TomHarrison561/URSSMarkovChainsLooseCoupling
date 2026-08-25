from Meanders import Meander


class SampleSpace:
    def __init__(self, n):
        self.n = n
        self.num_points = 2 * n

        self.all_matchings = self._generate_noncrossing_matchings(self.num_points)

        self.meanders = []
        self._build_meanders()

    def _generate_noncrossing_matchings(self, num_points):
        if num_points == 0:
            return [()]

        matchings = []
        for k in range(2, num_points + 1, 2):
            # Recurse inside (between 1 and k) and outside (after k)
            inside_matchings = self._generate_noncrossing_matchings(k - 2)
            outside_matchings = self._generate_noncrossing_matchings(num_points - k)

            for inside in inside_matchings:
                # Shift points inside by +1
                shifted_inside = tuple((u + 1, v + 1) for u, v in inside)
                for outside in outside_matchings:
                    # Shift points outside by +k
                    shifted_outside = tuple((u + k, v + k) for u, v in outside)

                    full_matching = ((1, k),) + shifted_inside + shifted_outside
                    matchings.append(full_matching)

        return matchings

    def _is_valid_meander(self, top, bottom):
        adj = {i: [] for i in range(1, self.num_points + 1)}

        for u, v in top:
            adj[u].append(v)
            adj[v].append(u)
        for u, v in bottom:
            adj[u].append(v)
            adj[v].append(u)

        visited = set()
        queue = [1]

        while queue:
            curr = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                queue.extend([neighbor for neighbor in adj[curr] if neighbor not in visited])

        # A meander forms a single closed loop traversing all 2n points
        return len(visited) == self.num_points

    def _build_meanders(self):
        seen = set()
        for top in self.all_matchings:
            for bottom in self.all_matchings:
                if self._is_valid_meander(top, bottom):
                    meander_obj = Meander(top=top, bottom=bottom)
                    # Deduplicate using the hashable Meander object
                    if meander_obj not in seen:
                        seen.add(meander_obj)
                        self.meanders.append(meander_obj)

    def __len__(self):
        return len(self.meanders)

    def __repr__(self):
        return f"SampleSpace(n={self.n}, total_meanders={len(self.meanders)})"