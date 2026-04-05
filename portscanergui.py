import socket
import threading
import time
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import concurrent.futures

# ---------------------------
# Service Map
# ---------------------------
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
    3306: 'MySQL', 3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-Alt'
}

# ---------------------------
# Scanner Worker
# ---------------------------
class PortScanner:
    def __init__(self, target, start_port, end_port, timeout=0.5, max_workers=500):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.max_workers = max_workers
        self._stop_event = threading.Event()

        self.total_ports = max(0, end_port - start_port + 1)
        self.scanned_count = 0
        self.open_ports = []            # list[(port, service)]
        self._lock = threading.Lock()
        self.result_queue = queue.Queue()

    def stop(self):
        self._stop_event.set()

    def _scan_port(self, port):
        if self._stop_event.is_set():
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target, port))
                if result == 0:
                    service = COMMON_PORTS.get(port, 'Unknown')
                    with self._lock:
                        self.open_ports.append((port, service))
                    self.result_queue.put(('open', port, service))
        except:
            pass # Ignore scan errors for minimal output
        finally:
            with self._lock:
                self.scanned_count += 1
            self.result_queue.put(('progress', self.scanned_count, self.total_ports))

    def resolve_target(self):
        return socket.gethostbyname(self.target)

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._scan_port, port): port for port in range(self.start_port, self.end_port + 1)}
            for future in concurrent.futures.as_completed(futures):
                if self._stop_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
        self.result_queue.put(('done', None, None))

# ---------------------------
# Minimal Tkinter GUI
# ---------------------------
class ScannerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Port Scanner - Minimal GUI")
        self.geometry("720x520")
        self.minsize(700, 500)

        self.scanner_thread = None
        self.scanner = None
        self.start_time = None
        self.poll_after_ms = 40

        self._build_ui()

    def _build_ui(self):
        # --- Top Frame: Scan Settings ---
        frm_top = ttk.LabelFrame(self, text="Scan Settings")
        frm_top.pack(fill="x", padx=10, pady=10)

        ttk.Label(frm_top, text="Target (IP / Hostname)").grid(row=0, column=0, padx=8, pady=15, sticky="e")
        self.ent_target = ttk.Entry(frm_top, width=35)
        self.ent_target.grid(row=0, column=1, padx=8, pady=15, sticky="w")

        ttk.Label(frm_top, text="Start Port").grid(row=0, column=2, padx=8, pady=15, sticky="e")
        self.ent_start = ttk.Entry(frm_top, width=10)
        self.ent_start.insert(0, "1")
        self.ent_start.grid(row=0, column=3, padx=8, pady=15, sticky="w")

        ttk.Label(frm_top, text="End Port:").grid(row=0, column=4, padx=8, pady=15, sticky="e")
        self.ent_end = ttk.Entry(frm_top, width=10)
        self.ent_end.insert(0, "1024")
        self.ent_end.grid(row=0, column=5, padx=8, pady=15, sticky="w")

        self.btn_start = ttk.Button(frm_top, text="Start Scan", command=self.start_scan)
        self.btn_start.grid(row=1, column=4, padx=8, pady=8, sticky="e")

        self.btn_stop = ttk.Button(frm_top, text="Stop", command=self.stop_scan, state="disabled")
        self.btn_stop.grid(row=1, column=5, padx=8, pady=8, sticky="w")

        for i in range(6):
            frm_top.grid_columnconfigure(i, weight=1)

        # --- Status Frame ---
        frm_status = ttk.LabelFrame(self, text="Status")
        frm_status.pack(fill="x", padx=10, pady=(0, 10))

        self.var_status = tk.StringVar(value="Idle")
        self.lbl_status = ttk.Label(frm_status, textvariable=self.var_status)
        self.lbl_status.pack(side="left", padx=10, pady=10)

        self.progress = ttk.Progressbar(frm_status, orient="horizontal", mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.var_elapsed = tk.StringVar(value="Elapsed: 0.00s")
        self.lbl_elapsed = ttk.Label(frm_status, textvariable=self.var_elapsed)
        self.lbl_elapsed.pack(side="right", padx=10, pady=10)

        # --- Results Area ---
        frm_results = ttk.LabelFrame(self, text="Open Ports")
        frm_results.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.txt_results = tk.Text(frm_results, height=15, wrap="none", font=("Consolas", 10))
        self.txt_results.pack(fill="both", expand=True, side="left", padx=10, pady=10)

        yscroll = ttk.Scrollbar(frm_results, orient="vertical", command=self.txt_results.yview)
        yscroll.pack(side="right", fill="y", pady=10)
        self.txt_results.configure(yscrollcommand=yscroll.set)

    def start_scan(self):
        if self.scanner_thread and self.scanner_thread.is_alive():
            return

        target = self.ent_target.get().strip()
        if not target:
            messagebox.showerror("Input Error", "Please enter a target address.")
            return

        try:
            start_port = int(self.ent_start.get().strip())
            end_port = int(self.ent_end.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Ports must be numeric.")
            return

        self.scanner = PortScanner(target, start_port, end_port)

        try:
            resolved_ip = self.scanner.resolve_target()
            self.append_text(f"Target: {target} ({resolved_ip})\n")
            self.append_text(f"Range: {start_port}-{end_port}\n\n")
        except Exception as e:
            messagebox.showerror("Resolution Error", f"Failed to resolve '{target}'.")
            return

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.clear_progress()

        self.start_time = time.time()
        self.var_status.set("Scanning...")
        self.update_elapsed()

        self.scanner_thread = threading.Thread(target=self.scanner.run, daemon=True)
        self.scanner_thread.start()
        self.after(self.poll_after_ms, self.poll_results)

    def stop_scan(self):
        if self.scanner:
            self.scanner.stop()
            self.var_status.set("Stopping...")

    def append_text(self, text):
        self.txt_results.insert(tk.END, text)
        self.txt_results.see(tk.END)

    def clear_progress(self):
        self.progress.configure(value=0, maximum=1)

    def update_elapsed(self):
        if self.start_time and self.var_status.get() in ("Scanning...", "Stopping..."):
            elapsed = time.time() - self.start_time
            self.var_elapsed.set(f"Elapsed: {elapsed:.2f}s")
            self.after(200, self.update_elapsed)

    def poll_results(self):
        if not self.scanner: return

        try:
            while True:
                msg_type, a, b = self.scanner.result_queue.get_nowait()
                if msg_type == 'open':
                    self.append_text(f"[+] Port {a} ({b}) is open\n")
                elif msg_type == 'progress':
                    self.progress.configure(maximum=b, value=a)
                elif msg_type == 'done':
                    total_open = len(self.scanner.open_ports)
                    self.append_text(f"\nScan complete.\n")
                    self.append_text(f"Open ports found: {total_open}\n")
                    self.var_status.set("Completed")
                    self.btn_start.configure(state="normal")
                    self.btn_stop.configure(state="disabled")
                    self.start_time = None
        except queue.Empty:
            pass

        if self.scanner_thread and self.scanner_thread.is_alive():
            self.after(self.poll_after_ms, self.poll_results)
        else:
            if self.var_status.get() in ("Scanning...", "Stopping..."):
                self.var_status.set("Completed")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

if __name__ == "__main__":
    app = ScannerGUI()
    app.mainloop()
