from PyQt6.QtCore import QRunnable, QObject, pyqtSignal
import socket
import requests
import ipaddress
import json
import os
import re
import time
import scapy.all as scapy
import netifaces

class NetworkScannerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    log = pyqtSignal(str) 

class NetworkScanner(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = NetworkScannerSignals()
        self.mac_cache = {}
        self.oui_db = self.load_oui_database()

    def run(self):
        try:
            if scapy is None:
                raise ImportError("Scapy is not installed")
            devices = self.deep_network_scan()
            self.signals.result.emit(devices)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

    def deep_network_scan(self):
        devices = []
        try:
            ip_range = self.get_network_range()
            if not ip_range:
                return []

            self.signals.log.emit(f"Starting network scan on range: {ip_range}") 

            arp_request = scapy.ARP(pdst=ip_range)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            answered_list = scapy.srp(packet, timeout=5, verbose=False, retry=3)[0]

            arp_devices = []
            for element in answered_list:
                ip = element[1].psrc
                mac = element[1].hwsrc
                self.mac_cache[ip] = mac
                arp_devices.append(ip)

            self.signals.log.emit(f"ARP scan complete. Found {len(arp_devices)} devices.") 

            ping_devices = self.ping_sweep(ip_range)

            self.signals.log.emit(f"ICMP ping sweep complete. Found {len(ping_devices)} devices.") 

            all_ips = list(set(arp_devices + ping_devices))

            total_ips = len(all_ips)
            for index, ip in enumerate(all_ips):
                try:
                    self.signals.log.emit(f"Processing device: {ip}") 
                    mac = self.get_mac(ip)
                    name = self.get_device_name(ip)
                    vendor = self.get_vendor(mac)
                    

                    devices.append({
                        "ip": ip,
                        "mac": mac,
                        "name": name,
                        "vendor": vendor
                    })

                    progress = int((index + 1) / total_ips * 100)
                    self.signals.progress.emit(progress)
                    self.signals.log.emit(f"Processed device: {ip}, Name: {name}, Vendor: {vendor}") 
                except:
                    continue

            return devices
        except Exception as e:
            self.signals.error.emit(f"Deep scan failed: {e}")
            return []

    def get_network_range(self):
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr['addr']
                        if not ip.startswith('127.'):
                            netmask = addr['netmask']
                            cidr = sum([bin(int(x)).count('1') for x in netmask.split('.')])
                            return f"{ip}/{cidr}"
            return None
        except Exception as e:
            print(f"Error determining network range: {e}")
            return None

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
            return None
        except Exception as e:
            print(f"MAC lookup failed for {ip}: {e}")
            return None

    def get_device_name(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return "Unknown"

    def get_vendor(self, mac):
        if not mac:
            return "Unknown"
        oui = mac[:8].upper()
        return self.oui_db.get(oui, "Unknown")

    
    def ping_sweep(self, ip_range):
        live_hosts = []
        try:
            ans, unans = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.IP(dst=ip_range)/scapy.ICMP(),
                                   timeout=2, verbose=False)
            for snd, rcv in ans:
                live_hosts.append(rcv[scapy.IP].src)
        except:
            pass
        return live_hosts

    def load_oui_database(self):
        OUI_FILE = "oui.json"
        OUI_URL = "http://standards-oui.ieee.org/oui/oui.txt"

        if not os.path.exists(OUI_FILE):
            return self.update_oui_database(OUI_FILE, OUI_URL)

        try:
            with open(OUI_FILE, 'r') as f:
                return json.load(f)
        except:
            return self.update_oui_database(OUI_FILE, OUI_URL)

    def update_oui_database(self, OUI_FILE, OUI_URL):
        try:
            response = requests.get(OUI_URL)
            oui_data = response.text

            ouis = {}
            pattern = re.compile(r"([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+$$hex$$\s+(.+)")

            for line in oui_data.split('\n'):
                match = pattern.search(line)
                if match:
                    oui = match.group(1).replace('-', ':').upper()
                    vendor = match.group(2).strip()
                    ouis[oui] = vendor

            with open(OUI_FILE, 'w') as f:
                json.dump(ouis, f)

            return ouis
        except Exception as e:
            print(f"Failed to update OUI database: {e}")
            return {}

