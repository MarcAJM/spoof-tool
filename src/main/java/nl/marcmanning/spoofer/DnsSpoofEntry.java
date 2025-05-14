package nl.marcmanning.spoofer;

import javafx.beans.property.SimpleStringProperty;

public class DnsSpoofEntry {

    private SimpleStringProperty domainName;
    private SimpleStringProperty maliciousIp;

    public DnsSpoofEntry() {
        domainName = new SimpleStringProperty();
        maliciousIp = new SimpleStringProperty();
    }

    public DnsSpoofEntry(String domainName, String maliciousIp) {
        this.maliciousIp = new SimpleStringProperty(maliciousIp);
        this.domainName = new SimpleStringProperty(domainName);
    }

    public String getDomainName() {
        return domainName.get();
    }

    public void setDomainName(String domainName) {
        this.domainName.set(domainName);
    }

    public String getMaliciousIpAddress() {
        return maliciousIp.get();
    }

    public void setMaliciousIpAddress(String maliciousIp) {
        this.maliciousIp.set(maliciousIp);
    }

    public SimpleStringProperty domainNameProperty() {
        return domainName;
    }

    public SimpleStringProperty maliciousIpProperty() {
        return maliciousIp;
    }
}
