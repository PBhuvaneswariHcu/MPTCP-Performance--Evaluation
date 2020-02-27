#!/usr/bin/env python
#****************************************************************************#
#               MPTCP with 1-i/f Average Throughput testing                  #
#****************************************************************************#


import time
import os
import sys
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import dumpNodeConnections, quietRun
from subprocess import Popen, PIPE

cut_a_link = True 
test_duration = 30 # seconds
link_down = True
mptcp_enabled_test = True 

#enabling mptcp

def set_mptcp_enabled(mptcp_enabled):
    key = "net.mptcp.mptcp_enabled"
    value = 0
    if mptcp_enabled:
        value = 1
    p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    print "stdout=",stdout,"stderr=", stderr

def Mptcp():
    net = Mininet( cleanup=True )

    #add 5 hosts with mininet default IP 10.0.0.1 to 10.0.0.5 to the network topology
    h1 = net.addHost( 'h1')
    h2 = net.addHost( 'h2')
    h3 = net.addHost( 'h3')
    h4 = net.addHost( 'h4')
    h5 = net.addHost( 'h5')

    #add 1 switch to the topology
    s3 = net.addSwitch('s3')

    c0 = net.addController( 'c0' )

    #connect 5 hosts through a switch
    net.addLink( h1, s3, cls=TCLink , bw=1000 )
    net.addLink( h2, s3, cls=TCLink , bw=1000 )
    net.addLink( h5, s3, cls=TCLink , bw=1000 )
    net.addLink( h4, s3, cls=TCLink , bw=1000 )
    net.addLink( h3, s3, cls=TCLink , bw=1000 )
    net.addLink( h1, s3, cls=TCLink , bw=1000 )
    net.addLink( h2, s3, cls=TCLink , bw=1000 )
    net.addLink( h3, s3, cls=TCLink , bw=1000 )
    net.addLink( h4, s3, cls=TCLink , bw=1000 )
    net.addLink( h5, s3, cls=TCLink , bw=1000 )


    #Assign IP,prefix and interface name to 5 hosts second interfaces
    h1.setIP('192.168.1.1', prefixLen=24,  intf='h1-eth1')
    h2.setIP('192.168.1.2', prefixLen=24, intf='h2-eth1')
    h3.setIP('192.168.1.3',prefixLen=24,  intf='h3-eth1')
    h4.setIP('192.168.1.4',prefixLen=24,  intf='h4-eth1')
    h5.setIP('192.168.1.5',prefixLen=24,  intf='h5-eth1')

    net.start()
    print "Dumping host connections"
    dumpNodeConnections( net.hosts )
    
    print "Testing network connectivity"
    net.pingAll()
    print "Testing bandwidth between h1 and h4"
#CLI(net)
    time.sleep(1) # wait for net to startup
    print "\n"," "*5,"#"*40,"\n"," "*10,"STARTING\n"

    #cut second interfaces for h1(client) and h2(server)
    def under_testing():
	time.sleep(test_duration/3.0)
	if cut_a_link:
	    print "\n",'cutting link...',
	    print h1.intf('h1-eth1').ifconfig('down'),
	    print h2.intf('h2-eth1').ifconfig('down'),
	    print 'link down\n'
	time.sleep(test_duration/3.0)
    
    if link_down:
        set_mptcp_enabled(True)
	under_testing()
        
        #check first no.of interface and interface connectivity, link down
        h2_out = h1.cmdPrint('ifconfig')
        print "ping test output: %s\n" % h2_out
        h1_up_intf=h1.IP( intf='h1-eth0')
        print "Testing ping between h1:%s and h2" % h1_up_intf
        h2_out = h1.cmdPrint('ping -c 1 '+h2.IP()+' ')
        print "ping test output: %s\n" % h2_out
	time.sleep(test_duration/3.0)
        #CLI(net)

        print 'starting iperf server at: ',h2.IP()
        h2.cmd('iperf -s'+str(test_duration)+'> iperf_mptcp_server_log.txt & ')
	time.sleep(test_duration/5.0)
	print 'starting iperf client at',h1_up_intf,', connect to ',h2.IP()
	h1.cmd('iperf -n 2G -c '+h2.IP()+' >> iperf_mptcp_client_link_down_log.txt &')
	time.sleep(test_duration/1.2)
	print "\niperf client response:"
	print h1.cmd('cat iperf_mptcp_client_link_down_log.txt')
        h2.cmd('kill -9 %iperf')
	time.sleep(test_duration/3.0)
        CLI(net)


    net.stop()
    os.system("sudo mn -c")

print

if __name__ == '__main__':
    # Tell mininet to print useful information
    Mptcp()

