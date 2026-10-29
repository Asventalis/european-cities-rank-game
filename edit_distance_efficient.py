from typing import List, Tuple

def min_edit_alignment_linear(s: str, t: str, ins_cost: int = 1, del_cost: int = 1, sub_cost: int = 1):
    """
    Optimal global alignment via Hirschberg's algorithm (linear space).
    Returns:
        distance (int),
        aligned_s (str),  # '-' when there's a gap in s (i.e., insertion from t)
        aligned_t (str)   # '-' when there's a gap in t (i.e., deletion from s)
    Costs:
        ins_cost: cost to insert a character from t (gap in s)
        del_cost: cost to delete a character from s (gap in t)
        sub_cost: cost to substitute s[i] -> t[j] (0 if equal, else sub_cost)
    """
    def _nw_last_row(sa: str, tb: str) -> List[int]:
        # Last row of Needleman–Wunsch DP using O(len(tb)) space.
        m = len(tb)
        prev = [j * ins_cost for j in range(m + 1)]
        for si in sa:
            curr0 = prev0 = prev[0] + del_cost
            curr = [curr0] + [0] * m
            left = curr0
            for j, tj in enumerate(tb, start=1):
                cost_diag = prev[j - 1] + (0 if si == tj else sub_cost)
                cost_up   = prev[j] + del_cost
                cost_left = left + ins_cost
                val = min(cost_diag, cost_up, cost_left)
                curr[j] = val
                left = val
            prev = curr
        return prev

    def _base_align_len1(sa: str, tb: str) -> Tuple[str, str]:
        n, m = len(sa), len(tb)
        if n == 0:
            return "-" * m, tb
        if m == 0:
            return sa, "-" * n

        if n == 1:
            a = sa[0]
            # Option A: delete a, insert all tb
            cost_del = del_cost + m * ins_cost
            # Option B: substitute a with one tb[j], insert the rest
            best_sub = min((0 if a == b else sub_cost) for b in tb)
            j_best = min(range(m), key=lambda j: (0 if a == tb[j] else sub_cost))
            cost_sub = best_sub + (m - 1) * ins_cost
            if cost_del <= cost_sub:
                return a + "-" * m, "-" + tb
            else:
                return "-" * j_best + a + "-" * (m - j_best - 1), tb[:j_best] + tb[j_best] + tb[j_best+1:]

        # m == 1
        b = tb[0]
        cost_ins = ins_cost + n * del_cost
        best_sub = min((0 if a == b else sub_cost) for a in sa)
        i_best = min(range(n), key=lambda i: (0 if sa[i] == b else sub_cost))
        cost_sub = best_sub + (n - 1) * del_cost
        if cost_ins <= cost_sub:
            return sa + "-", "-" * n + b
        else:
            return sa[:i_best] + sa[i_best] + sa[i_best+1:], "-" * i_best + b + "-" * (n - i_best - 1)

    def _hirschberg(sa: str, tb: str) -> Tuple[str, str]:
        n, m = len(sa), len(tb)
        if n == 0:
            return "-" * m, tb
        if m == 0:
            return sa, "-" * n
        if n == 1 or m == 1:
            return _base_align_len1(sa, tb)

        i_mid = n // 2
        L = _nw_last_row(sa[:i_mid], tb)
        R = _nw_last_row(sa[i_mid:][::-1], tb[::-1])
        # Split point k that minimizes L[k] + R[m-k]
        k = min(range(m + 1), key=lambda j: L[j] + R[m - j])

        left_s, left_t = _hirschberg(sa[:i_mid], tb[:k])
        right_s, right_t = _hirschberg(sa[i_mid:], tb[k:])
        return left_s + right_s, left_t + right_t

    def _alignment_cost(al_s: str, al_t: str) -> int:
        cost = 0
        for a, b in zip(al_s, al_t):
            if a == b and a != '-':
                continue
            if a == '-':
                cost += ins_cost
            elif b == '-':
                cost += del_cost
            else:
                cost += sub_cost
        return cost

    al_s, al_t = _hirschberg(s, t)
    dist = _alignment_cost(al_s, al_t)
    return dist, al_s, al_t


# --- quick demo ---
if __name__ == "__main__":
    d, a1, a2 = min_edit_alignment_linear("buttanalabagasciadituamoglie", "battonatuamadrezoccolagravida")
    print(d)   # 3
    print(a1)  # kitten-
    print(a2)  # sitt-ing

    d, a1, a2 = min_edit_alignment_linear("intention", "execution")
    print(d)   # 5
    print(a1)  # inten-tion
    print(a2)  # e-xecution
