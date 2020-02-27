#!/usr/bin/env python
#****************************************************************************#
#                       TCP Average Throughput testing                       #
#****************************************************************************#

import time
import os
import sys
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import dumpNodeConnections, quietRun
from subprocess import Popen, PIPE

test_duration = 30 # seconds
tcp_on = True


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
    net.addLink( h3, s3, cls=TCLink , bw=1000 )
    net.addLink( h4, s3, cls=TCLink , bw=1000 )
    net.addLink( h5, s3, cls=TCLink , bw=1000 )


    net.start()
    print "Dumping host connections"
    dumpNodeConnections( net.hosts )
    
    print "Testing network connectivity"
    net.pingAll()
    print "Testing bandwidth between h1 and h4"
#CLI(net)
    time.sleep(1) # wait for net to startup 
    print "\n"," "*5,"#"*40,"\n"," "*10,"STARTING\n"

    #disable mptcp on hosts and it inturns tcp
    if tcp_on:
        
        set_mptcp_enabled(False)
        h2_out = h1.cmdPrint('ifconfig')

        #test connectivity of h1(client) to the h2(server) from both the interfaces.
        print "ping test output: %s\n" % h2_out
        h2_out = h1.cmdPrint('ping -c 1 '+h2.IP()+' ')
        print "ping test output: %s\n" % h2_out
 
        #give time to print ping output
        time.sleep(3)

        print 'starting iperf server at: ',h2.IP()
        h2.cmd('iperf -s'+str(test_duration)+'> iperf_mptcp_server_log.txt & ')
	time.sleep(test_duration/5.0)

	print 'starting iperf client at',h1.IP,', connect to ',h2.IP()
	h1.cmd('iperf -n 2G -c '+h2.IP()+' >> iperf_tcp_client_log.txt &')

        #give time to print iperf output
	time.sleep(test_duration/1.2)
	print "\niperf client response:"
	print h1.cmd('cat iperf_tcp_client_log.txt')
        h2.cmd('kill -9 %iperf')
	time.sleep(test_duration/3.0)

        #use CLI to check any commands or outputs
        CLI(net)

    net.stop()
    os.system("sudo mn -c")

print

if __name__ == '__main__':
    # Tell mininet to print useful information
    Mptcp()

