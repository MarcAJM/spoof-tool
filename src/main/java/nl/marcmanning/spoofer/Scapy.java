package nl.marcmanning.spoofer;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.application.Platform;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;

public class Scapy {

    private static final ProcessBuilder processBuilder = new ProcessBuilder();
    private static final String PYTHON_SCRIPTS_PATH = "src/main/java/nl/marcmanning/spoofer/python_scripts";
    private static Process sniffProcess;

    public static String getMacAddress(String ipAddress) {
        List<String> command = new ArrayList<>(List.of("python3", PYTHON_SCRIPTS_PATH + "/get_mac.py", ipAddress));
        return execute(command);
    }

    public static void sendArpReply(String victimIp, String victimMac, String spoofIp, String attackerMac) {
        List<String> command = new ArrayList<>(List.of(
                "python3", PYTHON_SCRIPTS_PATH + "/send_arp_reply.py", victimIp, victimMac, spoofIp, attackerMac)
        );
        try {
            processBuilder.command(command);
            Process process = processBuilder.start();
            process.waitFor();
        } catch(Exception e) {
            System.out.println(e.getMessage());
        }
    }

    public static void sniff() {
        if (sniffProcess != null && sniffProcess.isAlive()) return;
        List<String> command = List.of("python3", PYTHON_SCRIPTS_PATH + "/sniff.py");
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            sniffProcess = processBuilder.start();
        } catch (Exception e) {
            System.out.println("Failed to start sniffer: " + e.getMessage());
        }
    }

    public static void stopSniffing() {
        if (sniffProcess != null && sniffProcess.isAlive()) {
            sniffProcess.destroy();
        }
    }

    private static String execute(List<String> command) {
        String result = "";
        try {
            processBuilder.command(command);
            Process process = processBuilder.start();

            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line);
            }
            process.waitFor();
            result = output.toString();
        } catch(Exception e) {
            System.out.println(e.getMessage());
        }
        return result;
    }
}