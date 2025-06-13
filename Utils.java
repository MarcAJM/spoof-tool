package nl.marcmanning.spoofer;

import javafx.beans.binding.Bindings;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFormatter;
import javafx.scene.input.KeyCode;
import nl.marcmanning.spoofer.components.JsonTableView;

public class Utils {

    public static boolean isValidIPv4(String ip) {
        return ip.matches("^((25[0-5]|2[0-4]\\d|1\\d{2}|[1-9]?\\d)(\\.|$)){4}");
    }

    public static void allowOnlyNumbersAndDots(TextField field) {
        field.setTextFormatter(new TextFormatter<String>(change -> {
            String text = change.getControlNewText();
            if (!text.matches("[0-9.]*")) {
                return null;
            }
            return change;
        }));
    }

    public static void disableAddingWhenEmpty(Button button, TextField field1, TextField field2) {
        button.disableProperty().bind(
                Bindings.or(
                        field1.textProperty().isEmpty(),
                        field2.textProperty().isEmpty()
                )
        );
    }

    public static <T> void addRemovingFunctionalityToTable(JsonTableView<T> table) {
        table.setOnKeyPressed(event -> {
            if (event.getCode() == KeyCode.BACK_SPACE) {
                T entry = table.getSelectionModel().getSelectedItem();
                if (entry != null) {
                    table.remove(entry);
                }
            }
        });
    }
}
