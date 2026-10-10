
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    interface Thrower { void run() throws Exception; }
    static boolean throwsType(Thrower t, Class<?> type) {
        try { t.run(); } catch (Exception e) { return type.isInstance(e); }
        return false;
    }
    public static void main(String[] a) {
        BankAccount x = new BankAccount(100), y = new BankAccount(0);
        x.deposit(50); check(x.getBalance() == 150, "deposit");
        x.withdraw(30); check(x.getBalance() == 120, "withdraw");
        check(throwsType(() -> x.withdraw(1000), IllegalStateException.class), "insuficiente");
        check(x.getBalance() == 120, "saldo intacto");
        check(throwsType(() -> x.deposit(0), IllegalArgumentException.class), "deposit 0");
        check(throwsType(() -> x.withdraw(-5), IllegalArgumentException.class), "withdraw neg");
        check(throwsType(() -> new BankAccount(-1), IllegalArgumentException.class), "ctor neg");
        x.transfer(y, 20); check(x.getBalance() == 100 && y.getBalance() == 20, "transfer");
        check(throwsType(() -> x.transfer(y, 500), IllegalStateException.class), "transfer insuficiente");
        check(x.getBalance() == 100 && y.getBalance() == 20, "nada muda");
        check(throwsType(() -> x.transfer(x, 1), IllegalArgumentException.class), "mesma conta");
        System.out.println("OK");
    }
}
