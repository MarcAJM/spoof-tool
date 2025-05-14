package nl.marcmanning.spoofer.components;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.scene.control.TableView;

import java.io.File;
import java.io.IOException;
import java.util.List;

public class JsonTableView<S> extends TableView<S> {

    private File file;
    private final ObjectMapper mapper;

    public JsonTableView() {
        super();
        this.mapper = new ObjectMapper();
    }

    public void setFile(File file) {
        this.file = file;
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
