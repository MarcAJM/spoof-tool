package nl.marcmanning.spoofer;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.collections.ListChangeListener;
import javafx.collections.ObservableList;
import nl.marcmanning.spoofer.components.LogView;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;

public class SpoofSession {

    private volatile boolean isRunning;
    private final LogView logView;
    private final ObjectMapper mapper;
    private final List<String> toBeSendMessages;
    ObservableList<TargetEntry> targets;

    private PrintWriter out;
    private BufferedReader in;

    private Process pythonProcess;
    private Path temp;

    public SpoofSession(LogView logView, ObservableList<TargetEntry> targets) {
        this.logView = logView;
        this.isRunning = false;
        this.mapper = new ObjectMapper();
        this.toBeSendMessages = new ArrayList<>();
        this.targets = targets;

        /* When a target gets added or removed, let python know. */
        targets.addListener((ListChangeListener<TargetEntry>) change -> {
            while (change.next()) {
                if (change.wasAdded()) {
                    for (TargetEntry target : change.getAddedSubList()) {
                        outputMessage(createAddTargetMessage(target));
                    }
                }
                if (change.wasRemoved()) {
                    for (TargetEntry target : change.getRemoved()) {
                        outputMessage(createRemoveTargetMessage(target));
                    }
                }
            }
        });
    }

    public void start() {
        if (!isRunning) {
            isRunning = true;
            for (TargetEntry target : targets) {
                String msg = createAddTargetMessage(target);
                toBeSendMessages.add(msg);
            }
            Thread thread = new Thread(() -> {
                if (!this.init()) return;

                /* Let python know of all the messages */
                for (String msg : toBeSendMessages) {
                    outputMessage(msg);
                }
                toBeSendMessages.clear();

                listen();
            });
            thread.setDaemon(true);
            thread.start();
        }
    }

    public void stop() {
        try {
            if (out != null) {
                out.println("{\"action\": \"shutdown\"}");
                out.flush();
            }
            if (out != null) out.close();
            if (in != null) in.close();
        } catch (IOException e) {
            logView.logError(e.getMessage());
        }
        stopSpoofer();
        if (temp != null)  temp.toFile().deleteOnExit();
        isRunning = false;
    }

    /* Start a server socket and also connect to it */
    private boolean init() {
        startSpoofer();
        out = new PrintWriter(pythonProcess.getOutputStream());
        in = new BufferedReader(new InputStreamReader(pythonProcess.getInputStream()));
        return true;
    }

    /* Listen for incoming messages */
    private void listen() {
        try {
            String line;
            while ((line = in.readLine()) != null) {
                JsonNode node = mapper.readTree(line);
                handleMessage(node);
            }
        } catch(IOException e) {
            logView.logError(e.getMessage());
        }
    }

    /* Handle message accordingly depending on the type */
    private void handleMessage(JsonNode node) {
        String type = node.has("type") ? node.get("type").asText() : "";

        switch (type) {
            case "packet" -> handlePacketMessage(node);
            case "info" -> {
                String msg = node.get("info").asText();
                logView.logInfo(msg);
            }
            case "error" -> {
                String msg = node.get("error").asText();
                logView.logError(msg);
            }
        }
    }

    private void handlePacketMessage(JsonNode json) {
//        String timestamp = json.has("timestamp") ? json.get("timestamp").asText() : "N/A";
//        String srcIp = json.has("src_ip") ? json.get("src_ip").asText() : "N/A";
//        String dstIp = json.has("dst_ip") ? json.get("dst_ip").asText() : "N/A";
        String summary = json.has("summary") ? json.get("summary").asText() : "";

        String message = String.format("""
        Packet Received:
        • Summary  : %s
        """, summary);

        logView.logInfo(message);
    }

    private void outputMessage(String msg) {
        if (out != null) {
            out.println(msg);
            out.flush();
        }
    }

    private void startSpoofer() {
        if (pythonProcess != null && pythonProcess.isAlive()) return;
        try (InputStream in = SpoofSession.class.getResourceAsStream("scripts/spoof.py")) {
            if (in == null) {
                logView.logError("Could not find spoof.py in resources.");
                return;
            }
            temp = Files.createTempFile("spoof", ".py");
            Files.copy(in, temp, StandardCopyOption.REPLACE_EXISTING);
            List<String> command = new ArrayList<>(List.of("python3", temp.toAbsolutePath().toString()));
            ProcessBuilder processBuilder = new ProcessBuilder();
            processBuilder.command(command);
            pythonProcess = processBuilder.start();

        } catch (IOException e) {
            logView.logError(e.getMessage());
        }
    }

    private void stopSpoofer() {
        if (pythonProcess != null && pythonProcess.isAlive()) {
            pythonProcess.destroy();
        }
    }

    private String createAddTargetMessage(TargetEntry target) {
        return String.format(
                "{\"action\": \"add_target\", \"ip1\": \"%s\", \"ip2\": \"%s\"}",
                target.getIp1(), target.getIp2()
        );
    }

    private String createRemoveTargetMessage(TargetEntry target) {
        return String.format(
                "{\"action\": \"remove_target\", \"ip1\": \"%s\", \"ip2\": \"%s\"}",
                target.getIp1(), target.getIp2()
        );
    }
}
