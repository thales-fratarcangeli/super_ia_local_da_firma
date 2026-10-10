public class BankAccount {
    private double balance;
    public BankAccount(double initialBalance) {
        if (initialBalance < 0) throw new IllegalArgumentException("negative");
        balance = initialBalance;
    }
    public double getBalance() { return balance; }
    public void deposit(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount");
        balance += amount;
    }
    public void withdraw(double amount) {
        if (amount <= 0) throw new IllegalArgumentException("amount");
        if (amount > balance) throw new IllegalStateException("insufficient");
        balance -= amount;
    }
    public void transfer(BankAccount to, double amount) {
        if (to == this) throw new IllegalArgumentException("same account");
        withdraw(amount);
        to.deposit(amount);
    }
}
