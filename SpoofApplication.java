package nl.marcmanning.spoofer;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.io.IOException;

public class SpoofApplication extends Application {

    @Override
    public void start(Stage stage) throws IOException {
        FXMLLoader fxmlLoader = new FXMLLoader(SpoofApplication.class.getResource("spoofer-view.fxml"));
        Scene scene = new Scene(fxmlLoader.load(), 480, 320);
        stage.setTitle("Spoofer");
        stage.setScene(scene);
        stage.show();
    }

    public static void main(String[] args) {
        launch();
    }
}