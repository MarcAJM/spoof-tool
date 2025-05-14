package nl.marcmanning.spoofer.components;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.Node;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.StackPane;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import javafx.scene.paint.Color;

/**
 * A clean and styled log display for JavaFX applications.
 */
public class LogView extends StackPane {

    private final TextFlow textFlow;
    private final ScrollPane scrollPane;

    public LogView() {
        textFlow = new TextFlow();
        textFlow.setLineSpacing(4);
        textFlow.setPadding(new Insets(10));
        textFlow.setPrefWidth(600);

        scrollPane = new ScrollPane(textFlow);
        scrollPane.setFitToWidth(true);
        scrollPane.setPrefHeight(300);
        scrollPane.setVbarPolicy(ScrollPane.ScrollBarPolicy.ALWAYS);
        scrollPane.setStyle("-fx-background: #1e1e1e;");

        this.getChildren().add(scrollPane);
        this.setStyle("-fx-background-color: #1e1e1e;");
    }

    public void logInfo(String message) {
        append("INFO", message, Color.LIGHTGREEN);
    }

    public void logError(String message) {
        append("ERROR", message, Color.INDIANRED);
    }

    public void logDebug(String message) {
        append("DEBUG", message, Color.DODGERBLUE);
    }

    public void log(String tag, String message, Color color) {
        append(tag, message, color);
    }

    private void append(String tag, String message, Color tagColor) {
        Platform.runLater(() -> {
            Text tagText = new Text("[" + tag + "] ");
            tagText.setFill(tagColor);
            tagText.setFont(Font.font("Consolas", FontWeight.BOLD, 12));

            Text contentText = new Text(message + "\n");
            contentText.setFill(Color.LIGHTGRAY);
            contentText.setFont(Font.font("Consolas", FontWeight.NORMAL, 12));

            textFlow.getChildren().addAll(tagText, contentText);

            // Auto-scroll to bottom
            scrollToBottom();
        });
    }

    private void scrollToBottom() {
        // Wait for layout pass, then scroll
        Platform.runLater(() -> scrollPane.setVvalue(1.0));
    }

    public void clear() {
        Platform.runLater(() -> textFlow.getChildren().clear());
    }

    public Node getView() {
        return this;
    }
}
