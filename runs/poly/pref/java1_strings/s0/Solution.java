public class Solution {
    static boolean isPalindrome(String s) {
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) if (Character.isLetterOrDigit(c)) b.append(Character.toLowerCase(c));
        return b.toString().contentEquals(new StringBuilder(b).reverse());
    }
    static String compress(String s) {
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < s.length(); ) {
            int j = i;
            while (j < s.length() && s.charAt(j) == s.charAt(i)) j++;
            out.append(s.charAt(i));
            if (j - i > 1) out.append(j - i);
            i = j;
        }
        return out.toString();
    }
}
