#!/usr/bin/env python
#****************************************************************************#
#             MPTCP 4-hosts 2-i/f Average Throughput testing                 #
#****************************************************************************#

import time
import os
import sys
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import dumpNodeConnections, quietRun
from subprocess import Popen, PIPE
from multiprocessing.dummy import Pool



test_duration = 120 # seconds
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
    s3 = net.addSwitch( 's3' )

    c0 = net.addController( 'c0' )

    #connect 5 hosts through a switch
    net.addLink( h1, s3, cls=TCLink , bw=1000 )
    net.addLink( h2, s3, cls=TCLink , bw=1000 )
    net.addLink( h3, s3, cls=TCLink , bw=1000 )
    net.addLink( h4, s3, cls=TCLink , bw=1000 )
    net.addLink( h5, s3, cls=TCLink , bw=1000 )
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

    #enable mptcp on hosts
    if mptcp_enabled_test:

        set_mptcp_enabled(True)
       
        #test connectivity of h1,h3,h4,h5(client) to the h2(server) from both the interfaces. 
        h2_out = h1.cmdPrint('ping -c 1 '+h2.IP('h2-eth0')+' ')
	h2_out2 = h1.cmdPrint('ping -c 1 '+h2.IP('h2-eth1')+' ')
        print "ping test output: %s\n" % h2_out
	print "ping test output: %s\n" % h2_out2

        
        h2_out = h3.cmdPrint('ping -c 1 '+h2.IP('h2-eth0')+' ')
	h2_out2 = h3.cmdPrint('ping -c 1 '+h2.IP('h2-eth1')+' ')
        print "ping test output: %s\n" % h2_out
	print "ping test output: %s\n" % h2_out2

       
        h2_out = h4.cmdPrint('ping -c 1 '+h2.IP('h2-eth0')+' ')
	h2_out2 = h4.cmdPrint('ping -c 1 '+h2.IP('h2-eth1')+' ')
        print "ping test output: %s\n" % h2_out
	print "ping test output: %s\n" % h2_out2


        h2_out = h5.cmdPrint('ping -c 1 '+h2.IP('h2-eth0')+' ')
	h2_out2 = h5.cmdPrint('ping -c 1 '+h2.IP('h2-eth1')+' ')
        print "ping test output: %s\n" % h2_out
	print "ping test output: %s\n" % h2_out2

        #give time to print ping output
	time.sleep(3)

        print 'starting iperf server at: ',h2.IP()
        h2.cmd('iperf -s > iperf_mptcp_server_log.txt & ')
	time.sleep(3)

        #create pool of 5 processes to send data from 4-clients to server simultaniously 
        p = Pool(5)
	i = 0
        lst = [[h, h2,] for h in [h1, h3, h4, h5]]
        main_list = []
	for l in lst:
            i += 1
            l.append(i)
            t = tuple(l)
            main_list.append(t)
        print(main_list)
        
        print(p.map(wrap_fn, main_list))

        h2.cmd('kill -9 %while')
        time.sleep(test_duration/12)

        CLI(net)

    net.stop()
    os.system("sudo mn -c")

def wrap_fn(args):
    return fn(*args)

#to run iperf by each process seperately 
def fn(h, server, i):
    print 'starting iperf client at',h.IP(),', connect to ',server.IP()
    h.cmd('iperf -n 2G -c '+ server.IP() +' >> iperf_mptcp_client'+ str(i) +'_log.txt &')

    #give time to print iperf output
    time.sleep(test_duration/2.0)
    print "\niperf client"+ str(i) +" response:"
    print h.cmd('cat iperf_mptcp_client'+ str(i) +'_log.txt')
    time.sleep(test_duration/10)
    return i
    print h, server, i

if __name__ == '__main__':
    # Tell mininet to print useful information
    Mptcp()

