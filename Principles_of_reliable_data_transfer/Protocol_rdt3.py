# Author:Pranav Tambe
#Author : Nishant Sing

import simpy
import random
from Packet import Packet
import sys

# the sender can be in one of these two states:
WAITING_FOR_CALL_FROM_ABOVE0 =0
WAIT_FOR_ACK0=1
WAITING_FOR_CALL_FROM_ABOVE1 =2
WAIT_FOR_ACK1=3
 
	
	
	
	

class rdt_Sender(object):
    def __init__(self,env):
        # additional timer-related variables
        # Initialize variables
        self.env=env 
        self.channel=None
        
        # some state variables
        self.state = WAITING_FOR_CALL_FROM_ABOVE0
        self.seq_num=0
        self.packet_to_be_sent=None
        self.timeout_value=3*2

        self.timer_is_running=False
        self.timer=None
        self.t1=0
        self.t2=0
        self.total=0
        self.t=0
        # This function models a Timer's behavior.
    def timer_behavior(self):
        try:
            # Start
            self.timer_is_running=True
            yield self.env.timeout(self.timeout_value)
            # Stop
            self.timer_is_running=False
            # take some actions
            self.timeout_action()
        except simpy.Interrupt:
            # upon interrupt, stop the timer
            self.timer_is_running=False
    
    # This function can be called to start the timer
    def start_timer(self):
        assert(self.timer_is_running==False)
        self.timer=self.env.process(self.timer_behavior())
        # This function can be called to stop the timer
    def stop_timer(self):
        assert(self.timer_is_running==True)
        self.timer.interrupt()
    def timeout_action(self):
        self.channel.udt_send(self.packet_to_be_sent)
        self.start_timer()

        
        # add here the actions to be performed
        # upon a timeout
    def rdt_send(self,msg):

            if self.state==WAITING_FOR_CALL_FROM_ABOVE0:
                # This function is called by the 
                # sending application.
                
                # create a packet, and save a copy of this packet
                # for retransmission, if needed
                self.packet_to_be_sent = Packet(seq_num=0, payload=msg)
                self.seq_num=1
                # send it over the channel
                self.channel.udt_send(self.packet_to_be_sent)
                # wait for an ACK or NAK
                #self.stop_timer()
                """ if(self.timer_is_running==True):
                    self.stop_timer
                    self.timeout_action() """
                self.start_timer()
                self.t1=self.env.now
                self.state=WAIT_FOR_ACK0
                return True
            elif self.state==WAITING_FOR_CALL_FROM_ABOVE1:
                # This function is called by the 
                # sending application.
                
                # create a packet, and save a copy of this packet
                # for retransmission, if needed
                self.packet_to_be_sent = Packet(seq_num=1, payload=msg)
                self.seq_num=0
                # send it over the channel
                self.channel.udt_send(self.packet_to_be_sent)
                # wait for an ACK or NAK
                #self.stop_timer()
                # if(self.timer_is_running==True):
                #     self.stop_timer
                self.start_timer()
                self.t1=self.env.now
                self.state=WAIT_FOR_ACK1
                return True
            else:
                return False
    def rdt_rcv(self,packt):
            # This function is called by the lower-layer 
            # when an ACK/NAK packet arrives
            assert(self.state==WAIT_FOR_ACK0 or self.state==WAIT_FOR_ACK1)
            if(not packt.corrupted and packt.payload=="ACK0" and self.seq_num==1 and self.timer_is_running):
                self.t2=self.env.now
                self.total+=self.t2-self.t1

                # Received an ACK. Everything's fine.
                self.stop_timer()
                self.t+=1
                self.state=WAITING_FOR_CALL_FROM_ABOVE1
                return True
                
            elif(not packt.corrupted and packt.payload=="ACK1" and self.seq_num==0 and self.timer_is_running):
                # Received a NAK. Need to resend packet.
                self.t2=self.env.now
                self.total+=self.t2-self.t1
                self.stop_timer()
                self.t+=1
                # self.timeout_action()
                self.state=WAITING_FOR_CALL_FROM_ABOVE0
                return True
               

class rdt_Receiver(object):
    def __init__(self,env):
        # Initialize variables
        self.env=env 
        self.receiving_app=None
        self.channel=None
        self.seq_num=0
        self.state = WAITING_FOR_CALL_FROM_ABOVE0

    def rdt_rcv(self,packt):    
        if self.state==WAITING_FOR_CALL_FROM_ABOVE0:
            if (packt.corrupted or packt.seq_num==1):
                response = Packet(seq_num=1, payload="ACK1")
                # send it over the channel
                self.channel.udt_send(response)
            else:
                response =  Packet(seq_num=0, payload="ACK0") 
                # send it over the channel
                self.channel.udt_send(response)
                self.receiving_app.deliver_data(packt.payload)
                self.state=WAITING_FOR_CALL_FROM_ABOVE1
        elif self.state==WAITING_FOR_CALL_FROM_ABOVE1:
            if (packt.corrupted or packt.seq_num==0):
                response = Packet(seq_num=0, payload="ACK0")
                # send it over the channel
                self.channel.udt_send(response)
            else:
                response =  Packet(seq_num=1, payload="ACK1") 
                # send it over the channel
                self.channel.udt_send(response)
                self.receiving_app.deliver_data(packt.payload)
                self.state=WAITING_FOR_CALL_FROM_ABOVE0
 

 # Simulation Testbench
 
 
#test Bench for Graph
# # Create a simulation environment
# env=simpy.Environment()

# import simpy
# from Applications_1 import SendingApplication,ReceivingApplication
# from Channel_1 import UnreliableChannel
# from   Pranav_Tambe_Nishant_Singh_rdt3 import *
# import matplotlib.pyplot as plt
# import numpy as np


# arr=[]
# arrx=[]

# for i in range (0,100,5):
#     # Populate the simulation environment with objects:
#     sending_app	  = SendingApplication(env)
#     receiving_app = ReceivingApplication(env)
#     rdt_sender	  = rdt_Sender(env)
#     rdt_receiver  = rdt_Receiver(env)
#     channel_for_data  = UnreliableChannel(env=env,Pc=0,Pl=i/100.0,delay=2,name="DATA_CHANNEL")
#     channel_for_ack  = UnreliableChannel(env=env,Pc=0,Pl=i/100.0,delay=2,name="DATA_CHANNEL")
#     arrx.append(i/100.0)

#     sending_app.rdt_sender = rdt_sender
#     rdt_sender.channel = channel_for_data
#     channel_for_data.receiver = rdt_receiver
#     rdt_receiver.receiving_app = receiving_app
#     # ....backward path...for acks
#     rdt_receiver.channel = channel_for_ack
#     channel_for_ack.receiver = rdt_sender
    
#     env.run(until=((i+5)/5)*20000)
#     arr.append(sending_app.avg)

# print(arr)
# print(arrx)
# plt_1 = plt.figure(figsize=(30, 10))
# plt.plot(arrx,arr,'-o')
# plt.vlines(arrx,0, arr , colors='b', linestyles='-', lw=2)
# plt.title("T_avg V/S Pc")
# plt.xlabel('Pc ')
# plt.ylabel('T_avg ')
# plt.show()