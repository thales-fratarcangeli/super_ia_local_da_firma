
public class Test {
    static void check(boolean c, String m) { if (!c) { System.err.println("FALHOU: " + m); System.exit(1); } }
    public static void main(String[] a) throws Exception {
        Counter c = new Counter();
        Thread[] ts = new Thread[8];
        for (int i = 0; i < ts.length; i++) {
            ts[i] = new Thread(() -> { for (int k = 0; k < 200000; k++) c.increment(); });
            ts[i].start();
        }
        for (Thread t : ts) t.join();
        check(c.get() == 1600000L, "perdeu atualizacoes: " + c.get());
        c.add(-100); check(c.get() == 1599900L, "add");
        c.reset(); check(c.get() == 0, "reset");
        Thread[] us = new Thread[4];
        for (int i = 0; i < us.length; i++) { us[i] = new Thread(() -> { for (int k = 0; k < 100000; k++) c.add(2); }); us[i].start(); }
        for (Thread t : us) t.join();
        check(c.get() == 800000L, "add concorrente: " + c.get());
        System.out.println("OK");
    }
}
