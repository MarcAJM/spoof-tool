package nl.marcmanning.spoofer.components;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.scene.control.TableView;
import net.harawata.appdirs.AppDirs;
import net.harawata.appdirs.AppDirsFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class JsonTableView<S> extends TableView<S> {

    private File file;
    private final ObjectMapper mapper;

    public JsonTableView() {
        super();
        this.mapper = new ObjectMapper();
    }

    public void setFile(String fileName) {
        AppDirs appDirs = AppDirsFactory.getInstance();
        Path dir = Path.of(appDirs.getUserDataDir("Spoofer", null, "default"));
        try {
            Files.createDirectories(dir);
            Path filePath = dir.resolve(fileName);
            file = new File(filePath.toString());
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void add(S value) {
        try {
            List<S> values = getItems();
            values.add(value);
            mapper.writerWithDefaultPrettyPrinter().writeValue(file, values);
        } catch(IOException exception) {
            System.out.println(exception.getMessage());
        }
    }

    public void remove(S value) {
        try {
            List<S> values = getItems();
            values.remove(value);
            mapper.writerWithDefaultPrettyPrinter().writeValue(file, values);
        } catch(IOException exception) {
            System.out.println(exception.getMessage());
        }
    }

    public void load(TypeReference<List<S>> ref) {
        if (file.exists() && file.length() > 0) {
            try {
                List<S> values = mapper.readValue(file, ref);
                getItems().addAll(values);
            } catch(IOException exception) {
                System.out.println(exception.getMessage());
            }
        }
    }
}
