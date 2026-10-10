
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    public static void main(String[] a) {
        check(Solution.isPalindrome("A man, a plan, a canal: Panama"), "panama");
        check(!Solution.isPalindrome("race a car"), "race");
        check(Solution.isPalindrome(""), "vazio");
        check(Solution.isPalindrome(".,!"), "so simbolos");
        check(Solution.isPalindrome("12321"), "digitos");
        check(!Solution.isPalindrome("12345"), "digitos nao");
        check(Solution.compress("aaabcc").equals("a3bc2"), "c1");
        check(Solution.compress("").equals(""), "c2");
        check(Solution.compress("abc").equals("abc"), "c3");
        check(Solution.compress("zzzzzzzzzzzz").equals("z12"), "c4");
        check(Solution.compress("aabbaa").equals("a2b2a2"), "c5");
        System.out.println("OK");
    }
}
