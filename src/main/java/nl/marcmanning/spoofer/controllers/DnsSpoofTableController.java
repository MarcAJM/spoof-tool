package nl.marcmanning.spoofer.controllers;

import com.fasterxml.jackson.core.type.TypeReference;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import nl.marcmanning.spoofer.DnsSpoofEntry;
import nl.marcmanning.spoofer.components.JsonTableView;
import nl.marcmanning.spoofer.Utils;

import java.io.File;

public class DnsSpoofTableController {

    @FXML
    private JsonTableView<DnsSpoofEntry> dnsSpoofTable;

    @FXML
    private TableColumn<DnsSpoofEntry, String> domainNameColumn;

    @FXML
    private TableColumn<DnsSpoofEntry, String> maliciousIpColumn;

    @FXML
    private TextField domainNameField;

    @FXML
    private TextField maliciousIpField;

    @FXML
    private Button dnsAddButton;

    @FXML
    private Label dnsErrorLabel;


    @FXML
    private void onDnsSpoofEntryAdd() {
        String domainName = domainNameField.getCharacters().toString();
        String maliciousIp = maliciousIpField.getCharacters().toString();

        if (!(Utils.isValidIPv4(maliciousIp))) {
            dnsErrorLabel.setText("The given malicious IP address is not a valid one!");
            dnsErrorLabel.setVisible(true);
            return;
        } else {
            dnsErrorLabel.setVisible(false);
        }

        DnsSpoofEntry entry = new DnsSpoofEntry(domainName, maliciousIp);
        dnsSpoofTable.add(entry);
    }


    @FXML
    public void initialize() {
        domainNameColumn.setCellValueFactory(new PropertyValueFactory<>("domainName"));
        maliciousIpColumn.setCellValueFactory(new PropertyValueFactory<>("maliciousIp"));

        dnsSpoofTable.setFile(new File("storage/dns_spoof_entries.json"));
        dnsSpoofTable.load(new TypeReference<>() {});

        // Make sure that some character must be in both text fields in order to be able to add it
        Utils.disableAddingWhenEmpty(dnsAddButton, domainNameField, maliciousIpField);

        // Make sure that only numbers and dots can be entered
        Utils.allowOnlyNumbersAndDots(maliciousIpField);

        Utils.addRemovingFunctionalityToTable(dnsSpoofTable);
    }
}
