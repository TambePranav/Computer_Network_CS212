# SimPy model for the Reliable Data Transport (rdt) Protocol 2.0 (Using ACK and NAK)

#
# Sender-side (rdt_Sender)
#	- receives messages to be delivered from the upper layer 
#	  (SendingApplication) 
#	- Implements the protocol for reliable transport
#	 using the udt_send() function provided by an unreliable channel.
#
# Receiver-side (rdt_Receiver)
#	- receives packets from the unrealible channel via calls to its
#	rdt_rcv() function.
#	- implements the receiver-side protocol and delivers the collected
#	data to the receiving application.

# Author:Pranav Tambe



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
		# Initialize variables
		self.env=env 
		self.channel=None
		
		# some state variables
		self.state = WAITING_FOR_CALL_FROM_ABOVE0
		self.seq_num=0
		self.packet_to_be_sent=None
		
	
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
			self.state=WAIT_FOR_ACK1
			return True
		else:
			return False
	
	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK/NAK packet arrives
		assert(self.state==WAIT_FOR_ACK0 or self.state==WAIT_FOR_ACK1)
		if(packt.payload=="ACK0" and self.seq_num==1):
			# Received an ACK. Everything's fine.
			self.state=WAITING_FOR_CALL_FROM_ABOVE1
		elif(packt.payload=="ACK1" and self.seq_num==0):
			# Received a NAK. Need to resend packet.
			self.state=WAITING_FOR_CALL_FROM_ABOVE0
			#self.channel.udt_send(self.packet_to_be_sent)
		elif(packt.payload=="ACK0" or packt.corrupted  and self.seq_num==0):
			self.channel.udt_send(self.packet_to_be_sent)
			self.state=WAIT_FOR_ACK1
		elif(packt.payload=="ACK1" or packt.corrupted  and self.seq_num==1):
			self.channel.udt_send(self.packet_to_be_sent)
			self.state=WAIT_FOR_ACK0
		# elif(packt.corrupted and self.seq_num==1):
		# 	self.channel.udt_send(self.packet_to_be_sent)
		# 	self.state=WAIT_FOR_ACK0
		# elif(packt.corrupted and self.seq_num==0):
		# 	self.channel.udt_send(self.packet_to_be_sent)
		# 	self.state=WAIT_FOR_ACK1
		else:
			print("ERROR! rdt_rcv() was expecting an ACK or a NAK. Received a corrupted packet.")
			print("Halting simulation...")
			sys.exit(0)

			

class rdt_Receiver(object):
	def __init__(self,env):
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None
		self.seq_num_1=0
		

	def rdt_rcv(self,packt):
		# This function is called by the lower-layer when a packet arrives
		# at the receiver
		
		# check whether the packet is corrupted
		if(packt.corrupted):
			# send a NAK and discard this packet.
			f=(((self.seq_num_1)+1)%2)
			response = Packet(seq_num=0, payload=f"ACK{f}") #Note: seq_num for the response can be arbitrary. It is ignored.
			# send it over the channel
			self.channel.udt_send(response)
		elif  self.seq_num_1!=packt.seq_num:
			f=(((self.seq_num_1)+1)%2)
			response = Packet(seq_num=0, payload=f"ACK{f}")
			self.channel.udt_send(response)
		else:
			# The packet is not corrupted.
			# Send an ACK and deliver the data.
			f=(((self.seq_num_1)))
			response =  Packet(seq_num=0, payload=f"ACK{f}") 
			self.seq_num_1=((self.seq_num_1)+1)%2 
			# send it over the channel
			self.channel.udt_send(response)
			self.receiving_app.deliver_data(packt.payload)

