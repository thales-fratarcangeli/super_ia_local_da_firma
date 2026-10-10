
import java.util.Arrays;
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    public static void main(String[] a) {
        check(Arrays.equals(Solution.topK(new int[]{1,1,1,2,2,3}, 2), new int[]{1, 2}), "t1");
        check(Arrays.equals(Solution.topK(new int[]{4,4,5,5,6}, 2), new int[]{4, 5}), "desempate por valor");
        check(Arrays.equals(Solution.topK(new int[]{3,3,-1,-1,9}, 3), new int[]{-1, 3, 9}), "negativos");
        check(Arrays.equals(Solution.topK(new int[]{7,7,8}, 10), new int[]{7, 8}), "k grande");
        check(Solution.topK(new int[]{1,2}, 0).length == 0, "k zero");
        check(Solution.topK(new int[]{}, 3).length == 0, "vazio");
        System.out.println("OK");
    }
}
