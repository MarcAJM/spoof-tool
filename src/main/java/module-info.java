module nl.marcmanning.testapp {
    requires javafx.controls;
    requires javafx.fxml;
    requires com.fasterxml.jackson.databind;
    requires net.harawata.appdirs;


    opens nl.marcmanning.spoofer to javafx.fxml;
    exports nl.marcmanning.spoofer;
    exports nl.marcmanning.spoofer.controllers;
    opens nl.marcmanning.spoofer.controllers to javafx.fxml;
    exports nl.marcmanning.spoofer.components;
    opens nl.marcmanning.spoofer.components to javafx.fxml;
}