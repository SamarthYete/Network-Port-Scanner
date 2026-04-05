# Network-Port-Scanner

This is a professional README.md file tailored for your Python Port Scanner. It highlights the multi-threaded nature of the application, the GUI features, and includes a necessary ethical disclaimer.
# Multi-Threaded Network Port Scanner (GUI)
A high-performance, lightweight network utility built with **Python**, **Tkinter**, and **Concurrent Futures**. This tool allows users to scan a range of ports on a target IP or hostname to identify open services.
## 🚀 Features
 * **Fast Multi-Threading:** Utilizes ThreadPoolExecutor to scan hundreds of ports concurrently, significantly reducing scan time.
 * **Real-Time GUI Updates:** Built with Tkinter, featuring a live progress bar, elapsed time counter, and a scrollable results log.
 * **Service Detection:** Automatically identifies common services (e.g., SSH, HTTP, FTP, MySQL) based on standard port numbers.
 * **Safe Execution:** Includes a "Stop" functionality to safely terminate threads during an active scan.
 * **DNS Resolution:** Automatically resolves hostnames (e.g., google.com) to their respective IP addresses.
## 🛠️ Built With
 * Python 3.x
 * **Standard Libraries:** socket, threading, concurrent.futures, queue
 * **GUI:** tkinter (TTK themed)
## 📋 Prerequisites
Most Python installations include Tkinter by default. If you are on Linux and encounter an import error, you may need to install it:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

```
## 💻 Installation & Usage
 1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/port-scanner-gui.git
   cd port-scanner-gui
   
   ```
 2. **Run the application:**
   ```bash
   python scanner.py
   
   ```
 3. **How to use:**
   * Enter the **Target IP or Hostname** (e.g., 192.168.1.1 or scanme.nmap.org).
   * Define the **Start** and **End** port range.
   * Click **Start Scan**.
   * View open ports and their associated services in the results panel.
## ⚠️ Ethical Disclaimer
This tool is provided for **educational and ethical testing purposes only**.
Scanning networks without explicit permission is illegal in many jurisdictions. The developer assumes no liability for any misuse of this tool or damage caused by its application. Use it responsibly on networks you own or have permission to test.

