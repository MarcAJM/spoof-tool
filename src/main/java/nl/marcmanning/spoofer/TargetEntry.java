package nl.marcmanning.spoofer;

import javafx.beans.property.SimpleStringProperty;

import java.util.Objects;

public class TargetEntry {
    private final SimpleStringProperty ip1;
    private final SimpleStringProperty ip2;

    public TargetEntry() {
        ip1 = new SimpleStringProperty();
        ip2 = new SimpleStringProperty();
    }

    public TargetEntry(String ip1, String ip2) {
        this.ip1 = new SimpleStringProperty(ip1);
        this.ip2 = new SimpleStringProperty(ip2);
    }

    public String getIp1() {
        return ip1.get();
    }

    public SimpleStringProperty ip1Property() {
        return ip1;
    }

    public void setIp1(String ip1) {
        this.ip1.set(ip1);
    }

    public String getIp2() {
        return ip2.get();
    }

    public SimpleStringProperty ip2Property() {
        return ip2;
    }

    public void setIp2(String ip2) {
        this.ip2.set(ip2);
    }

    public boolean isEqual(TargetEntry entry) {
        return (Objects.equals(entry.getIp1(), getIp1()) && Objects.equals(entry.getIp2(), getIp2()))
                || (Objects.equals(entry.getIp1(), getIp2()) && Objects.equals(entry.getIp2(), getIp1()));
    }

    public TargetEntry copy() {
        return new TargetEntry(this.getIp1(), this.getIp2());
    }
}
