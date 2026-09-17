# 🔒 Network Port Scanner

> Multithreaded CLI network utility written in Python for scanning active TCP ports and auditing network service availability.

![Python](https://img.shields.io/badge/Python-Socket_Programming-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Cybersecurity](https://img.shields.io/badge/Domain-Cybersecurity-red?style=for-the-badge)

---

## ⭐ Star Schema (Security Audit Log Model)

```
                            +-----------------------------------+
                            |           Dim_TargetHost          |
                            +-----------------------------------+
                            | Host_Key (PK)                     |
                            | IP_Address                        |
                            | Hostname                          |
                            | Subnet                            |
                            +-----------------+-----------------+
                                              | 1
                                              |
                                              | N
+-----------------------+   +-----------------+-----------------+   +-----------------------+
|  Dim_Calendar         | 1 |      Fact_PortScanEvent           | 1 |  Dim_NetworkPort      |
+-----------------------+---+-----------------------------------+---+-----------------------+
| Date_Key (PK)         | N | Scan_Event_Key (PK)               | N | Port_Key (PK)         |
| Full_Date             |   | Date_Key (FK)                     |   | Port_Number (22, 80)  |
| Time_String           |   | Host_Key (FK)                     |   | Protocol (TCP/UDP)    |
+-----------------------+   | Port_Key (FK)                     |   | Default_Service_Name  |
                            | Is_Open_Flag (Measure)            |   +-----------------------+
                            | Latency_Ms (Measure)              |
                            | Banner_Grabbed_Len (Measure)      |
                            +-----------------------------------+
```

---

## 🚀 Usage

```bash
python port_scanner.py --target 192.168.1.1 --ports 1-1000 --threads 50
```
