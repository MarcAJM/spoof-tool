package nl.marcmanning.spoofer.controllers;

import javafx.fxml.FXML;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ChoiceBox;

public class SettingsController {

    @FXML
    private CheckBox sslCheckBox;

    @FXML
    private ChoiceBox<String> modeChoiceBox;

    @FXML
    private CheckBox dnsCheckBox;

    @FXML
    public void initialize() {
        modeChoiceBox.getItems().addAll("Silent", "All Out");
    }

}
