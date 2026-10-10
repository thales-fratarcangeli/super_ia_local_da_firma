import java.util.concurrent.atomic.AtomicLong;

public class Counter {
    private final AtomicLong v = new AtomicLong();
    public void increment() { v.incrementAndGet(); }
    public void add(int delta) { v.addAndGet(delta); }
    public long get() { return v.get(); }
    public void reset() { v.set(0); }
}
