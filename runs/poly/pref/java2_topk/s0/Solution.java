import java.util.*;

public class Solution {
    static int[] topK(int[] nums, int k) {
        if (k <= 0) return new int[0];
        Map<Integer, Integer> f = new HashMap<>();
        for (int n : nums) f.merge(n, 1, Integer::sum);
        List<Integer> keys = new ArrayList<>(f.keySet());
        keys.sort((x, y) -> f.get(y) != f.get(x).intValue() ? f.get(y) - f.get(x) : Integer.compare(x, y));
        int m = Math.min(k, keys.size());
        int[] out = new int[m];
        for (int i = 0; i < m; i++) out[i] = keys.get(i);
        return out;
    }
}
