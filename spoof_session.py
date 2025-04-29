import click
import utils

class SpoofSession:

    def __init__(self, victim_ip_address):
        self.is_running = True
        self.start()

    def start(self):
        while self.is_running:
            try:
                user_input = input("$ ").strip()
                if user_input in ["exit", "quit", "q"]:
                    self.is_running = False
                    utils.print_info_message("Stopped spoofing")
                    break
            except KeyboardInterrupt:
                click.echo()
                utils.print_error_message("Session interrupted")
                break

def find_mac_address(ip_address):
    print("TODO")