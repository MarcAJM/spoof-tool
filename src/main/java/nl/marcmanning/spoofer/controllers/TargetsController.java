package nl.marcmanning.spoofer.controllers;

import com.fasterxml.jackson.core.type.TypeReference;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import nl.marcmanning.spoofer.components.JsonTableView;
import nl.marcmanning.spoofer.TargetEntry;
import nl.marcmanning.spoofer.Utils;

import java.io.File;
import java.util.List;

public class TargetsController {

    @FXML
    private JsonTableView<TargetEntry> targetLinksTable;

    @FXML
    private TableColumn<TargetEntry, String> ip1Column;

    @FXML
    private TableColumn<TargetEntry, String> ip2Column;

    @FXML
    private Button targetAddButton;

    @FXML
    private TextField targetIp1Field;

    @FXML
    private TextField targetIp2Field;

    @FXML
    private Label targetsErrorLabel;

    @FXML
    private void onTargetAdd() {
        String ip1 = targetIp1Field.getText();
        String ip2 = targetIp2Field.getText();

        targetsErrorLabel.setVisible(false);
        if (!(Utils.isValidIPv4(ip1)) || !(Utils.isValidIPv4(ip2))) {
            targetsErrorLabel.setText("One of the given IP addresses is not a valid one!");
            targetsErrorLabel.setVisible(true);
            return;
        }

        TargetEntry entry = new TargetEntry(ip1, ip2);
        List<TargetEntry> entries = targetLinksTable.getItems();
        boolean alreadyExists = false;
        for (TargetEntry e : entries) {
            if (e.isEqual(entry)) {
                alreadyExists = true;
                break;
            }
        }
        if (alreadyExists) {
            targetsErrorLabel.setText("The target link already exists!");
            targetsErrorLabel.setVisible(true);
            return;
        }
        targetLinksTable.add(entry);
    }

    @FXML
    public void initialize() {
        ip1Column.setCellValueFactory(new PropertyValueFactory<>("ip1"));
        ip2Column.setCellValueFactory(new PropertyValueFactory<>("ip2"));

        targetLinksTable.setFile("target_links.json");
        targetLinksTable.load(new TypeReference<>() {});

        // Make sure that some character must be in both text fields in order to be able to add it
        Utils.disableAddingWhenEmpty(targetAddButton, targetIp1Field, targetIp2Field);

        // Make sure that only numbers and dots can be entered
        Utils.allowOnlyNumbersAndDots(targetIp1Field);
        Utils.allowOnlyNumbersAndDots(targetIp2Field);

        Utils.addRemovingFunctionalityToTable(targetLinksTable);
    }
}
