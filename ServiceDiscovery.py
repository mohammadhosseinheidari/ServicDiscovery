import subprocess
import re
import argparse
import socket
from typing import List, Union
from urllib.parse import urlparse

class ServiceDiscovery:
    def __init__(self, targets: Union[List[str], str]):
        self.targets_input = targets
        self.ips: List[str] = []
        self.masscan_output = "masscan-res.txt"
        self.ports = (
            "80,443,444,1443,1455,2000,2020,2052,2053,2082,2083,2086,2087,"
            "2095,2096,2222,3000,3003,3030,3300,3306,3333,4000,4040,4400,4440,"
            "4443,4444,4900,5000,5030,5050,5432,5500,5555,6000,6100,6666,7000,"
            "7007,7008,7700,7777,8000,8080,8090,8100,8180,8200,8300,8400,8443,"
            "8500,8600,8700,8800,8880,8888,8899,9000,9009,9040,9050,9080,9090,"
            "9100,9200,9300,9400,9500,9898,9900,9999,10443,27017"
        )

    def is_ip(self, s: str) -> bool:
        """Check if the string is a valid IP address"""
        return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", s) is not None

    def resolve_domain_to_ip(self, domain: str) -> str:
        """Resolve domain to IP address"""
        try:
            ip = socket.gethostbyname(domain)
            return ip
        except socket.gaierror:
            print(f"[!] Unable to resolve domain {domain}")
            return ""

    def check_cdn(self, ip: str) -> bool:
        """Check if the IP belongs to a CDN using cut-cdn"""
        cmd = f"cut-cdn -i {ip}"
        try:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0 and "CDN" in result.stdout.decode():
                return True
            else:
                return False
        except Exception as e:
            print(f"[!] Error checking CDN: {e}")
            return False

    def run_masscan(self, targets: List[str]):
        """Run masscan on IPs to discover open ports"""
        print("[*] Running masscan...")
        with open("ips.txt", "w") as f:
            f.write("\n".join(targets))
        
        cmd = [
            "masscan",
            "-iL", "ips.txt",
            "--open",
            "--ports", self.ports,
            "-oL", self.masscan_output
        ]
        subprocess.run(cmd)
        print(f"[+] Masscan results saved to {self.masscan_output}")

    def parse_masscan_results(self) -> List[str]:
        """Parse the masscan results and extract open ports"""
        print("[*] Parsing masscan results...")
        results = []
        with open(self.masscan_output, "r") as f:
            for line in f:
                if "open" in line:
                    parts = re.split(r"\s+", line)
                    ip = parts[3]
                    port = parts[2]
                    results.append(f"{ip}:{port}")
        print(f"[+] Found {len(results)} open ports.")
        return results

    def run_httpx(self, target: str, port: str):
        """Run httpx on a specific IP and port"""
        print(f"[*] Running httpx on {target}:{port}...")
        cmd = [
            "httpx",
            "-silent",
            "-follow-host-redirects",
            "-title",
            "-status-code",
            "-tech-detect",
            "-p", port
        ]
        try:
            result = subprocess.run(cmd, input=target.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(result.stdout.decode())
        except Exception as e:
            print(f"[!] Failed to run httpx: {e}")

    def run_httpx_on_all_ports(self, targets: List[str]):
        """Run httpx on all the open ports for the given IPs"""
        print("[*] Running httpx on open ports...")
        for target in targets:
            ip, port = target.split(":")
            self.run_httpx(ip, port)

    def handle_targets(self):
        """Handle the provided targets (IPs or domains)"""
        lines = []
        if isinstance(self.targets_input, list):
            lines = self.targets_input
        elif isinstance(self.targets_input, str):
            with open(self.targets_input, "r") as f:
                lines = f.read().splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # If it's a URL (starts with http:// or https://)
            if line.startswith("http://") or line.startswith("https://"):
                parsed_url = urlparse(line)
                domain = parsed_url.netloc
                print(f"[+] Domain detected: {domain}")
                ip = self.resolve_domain_to_ip(domain)
                if ip:
                    self.ips.append(ip)
                # Run httpx directly on the domain as well
                self.run_httpx(line, "")
            elif self.is_ip(line):
                # Direct IP Address
                self.ips.append(line)
            else:
                # Domain that doesn't start with http(s)://
                ip = self.resolve_domain_to_ip(line)
                if ip:
                    self.ips.append(ip)

    def run_all(self):
        """Run the complete service discovery process"""
        print("[*] Starting service discovery...")
        self.handle_targets()
        if not self.ips:
            print("[!] No valid IPs found. Exiting.")
            return

        # Separate the IPs to check if they need masscan or not
        non_cdns = []
        for ip in self.ips:
            if not self.check_cdn(ip):
                non_cdns.append(ip)

        if non_cdns:
            self.run_masscan(non_cdns)
            targets = self.parse_masscan_results()
            if targets:
                # Run httpx on the IPs with the open ports
                self.run_httpx_on_all_ports(targets)

        print("[✓] Done.")

def print_banner():
    banner = r"""
   ___              _           ____  _                                      
  / __| ___ _ _ ___| |_ ___ _ _|  _ \| |_  ___ _ __  ___ __ _ _ __ ___ _ _   
 | (_ |/ -_) '_/ -_)  _/ _ \ '_| | | | ' \/ -_) '  \/ -_) _` | '_/ _ \ ' \  
  \___|\___|_| \___|\__\___/_| |_| |_|_||_\___|_|_|_\___\__,_|_| \___/_||_|

        [~] Network Service Discovery Tool (masscan + httpx)
    """
    print(banner)


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="🕵️‍♂️ Simple Service Discovery Tool using masscan & httpx")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Path to input file (IPs, CIDRs, Domains)", type=str)
    group.add_argument("-t", "--target", help="Single IP or Domain (e.g., 1.1.1.1 or example.com)", type=str)

    args = parser.parse_args()

    if args.file:
        discovery = ServiceDiscovery(args.file)
    elif args.target:
        discovery = ServiceDiscovery([args.target])

    discovery.run_all()


if __name__ == "__main__":
    main()
