# trex

  ### flow
TREX LAN1發包給DUT  DUT會設Routing模式，LAN1收到後會從內部轉發給LAN2，DUT LAN2會再回傳封包給TREX的LAN2確認接收

       (TRex port 0)                        (TRex port 1)
    IP: 192.168.130.5/24                 IP: 192.168.47.19/24
          |                                     |
          |                                     |
         enp1s0 (DUT)                          enp2s0 (DUT)
     IP: 192.168.130.1/24                  IP: 192.168.47.18/24
              |                                     |
   Connected route:                          Connected route:
   192.168.130.0/24 → enp1s0                 192.168.47.0/24 → enp2s0
              |                                     |
      Static route:                          Static route:
  16.0.0.0/16 via 192.168.130.5         48.0.0.0/16 via 192.168.47.19

  ### (trex)關掉 IOMMU 測試
  #turbostat
  
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash intel_iommu=off processor.max_cstate=1 intel_idle.max_cstate=0"  

lspci -k | grep -A 3 Ethernet  #乙太網卡的 PCI 裝置資訊
sudo ./dpdk_setup_ports.py -t  #腳本驗證trex是否可以看到所需的接口

## 啟動Trex
TRex port0:  src=1.1.1.5   <------>  DUT enp1s0: 1.1.1.1
TRex port1:  src=2.2.2.5   <------>  DUT enp2s0: 2.2.2.2
TRex port0:  src=3.3.3.5   <------>  DUT enp1s0: 3.3.3.3
TRex port1:  src=4.4.4.5   <------>  DUT enp2s0: 4.4.4.4

### 設定 hugepages
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages   
cat /proc/meminfo | grep Huge
### set IP
sudo ip addr add 1.1.1.1/24 dev enp1s0
sudo ip addr add 2.2.2.2/24 dev enp2s0
sudo ip addr add 3.3.3.3/24 dev enp3s0
sudo ip addr add 4.4.4.4/24 dev enp4s0
### enable forwarding
sudo sysctl -w net.ipv4.ip_forward=1
### add routes
sudo ip route add 16.0.0.0/16 via 1.1.1.5 dev enp1s0
sudo ip route add 48.0.0.0/16 via 2.2.2.5 dev enp2s0
sudo ip route add 32.0.0.0/16 via 3.3.3.5 dev enp3s0
sudo ip route add 64.0.0.0/16 via 4.4.4.5 dev enp4s0
### 直接綁定 TRex 的 MAC
sudo arp -i enp1s0 -s 1.1.1.5 00:07:32:bf:6c:d0
sudo arp -i enp2s0 -s 2.2.2.5 00:07:32:bf:6c:d1
sudo arp -i enp3s0 -s 3.3.3.5 00:07:32:bf:6c:d2
sudo arp -i enp4s0 -s 4.4.4.5 00:07:32:bf:6c:d3
### 啟動 TRex 
sudo ./t-rex-64 -i
sudo ./trex-console

進trex-console
> portattr 
> start -f dual_port_test.p  #stop

> start -f stl/bench.py -p 0 1 -m 90% --force   //-m line rate
> start -f stl/throughput_test.py -p 0 1 --force
> stats
