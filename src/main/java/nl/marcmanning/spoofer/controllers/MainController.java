package nl.marcmanning.spoofer.controllers;

import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.TableView;
import javafx.scene.layout.BorderPane;
import nl.marcmanning.spoofer.DnsSpoofEntry;
import nl.marcmanning.spoofer.SpoofSession;
import nl.marcmanning.spoofer.TargetEntry;
import nl.marcmanning.spoofer.components.LogView;

public class MainController {

    private SpoofSession session;
    private boolean isRunning;

    @FXML
    private LogView logView;

    @FXML
    private Button playButton;

    @FXML
    private BorderPane targetsView;

    @FXML
    private BorderPane dnsSpoofTableView;

    private TableView<TargetEntry> targetsTable;
    private TableView<DnsSpoofEntry> dnsSpoofEntryTable;

    @FXML
    public void initialize() {
        targetsTable = (TableView<TargetEntry>) targetsView.getCenter();
        dnsSpoofEntryTable = (TableView<DnsSpoofEntry>) dnsSpoofTableView.getCenter();
        session = new SpoofSession(logView, targetsTable.getItems(), dnsSpoofEntryTable.getItems());
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            if (session != null) session.stop();
        }));

        isRunning = false;
        playButton.setOnMouseClicked(_ -> {
            isRunning = !isRunning;
            if (isRunning) {
                playButton.setText("Stop");
                session.start();
            } else {
                session.stop();
                playButton.setText("Play");
            }
        });
    }
}
