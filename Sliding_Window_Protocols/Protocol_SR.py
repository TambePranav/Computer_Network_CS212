""" Name:-Pranav Tambe
Roll No :-2106339 """

# include all necessary modules
import simpy
import random
import sys
from Packet import Packet

class rdt_Sender(object):
	
	def __init__(self, env):
		# Initialize variables and parameters
		self.env = env
		self.channel = None

		# some default parameter values
		self.data_packet_length = 10  # bits
		self.timeout_value = 10  # default timeout value for the sender
		self.N = 5 # Sender's Window size
		self.K = 16  # Packet Sequence numbers can range from 0 to K-1

		# some state variables and parameters for the Go-Back-N Protocol
		self.base = 1  # base of the current window
		self.nextseqnum = 1  # next sequence number
		self.sndpkt = {} # a buffer for storing the packets to be sent (implemented as a Python dictionary)

		# some other variables to maintain sender-side statistics
		self.total_packets_sent= 0
		self.num_retransmissions= 0
		
    #=====================================================================
		# Now for  SR we have timer for each packet
		self.timer = {} 
		self.timer_is_running = {} # To store the timer state 
  
		# store which acked packets
		self.acked = {} #acked_pkts
  #=====================================================================


		
	def rdt_send(self,msg):
		# This function is called by the upper-layer 
		# when a packet arrives at the sender
		if (self.nextseqnum in [(self.base+i)%self.K for i in range(0,self.N)]):
			# print("TIME:",self.env.now,"RDT_SENDER: rdt_send() called for nextseqnum=",self.nextseqnum," within current window. Sending new packet.")
			# create a new packet and store a copy of it in the buffer
			Packet_for_sending = Packet(seq_num=self.nextseqnum, payload=msg, packet_length=self.data_packet_length)
			self.sndpkt[self.nextseqnum]=Packet_for_sending
			# send the packet
			self.channel.udt_send(Packet_for_sending)
			self.total_packets_sent+=1
			# start the timer
			# self.timer[self.nextseqnum]=self.env.timeout(self.timeout_value)
			self.start_timer(self.nextseqnum)
			# update nextseqnum
			self.nextseqnum=(self.nextseqnum+1)%self.K
			return True
		else:
			# self.buffer.append(Packet(seq_num=self.nextseqnum, payload=msg, packet_length=self.data_packet_length))
			# # update nextseqnum
			# self.nextseqnum = (self.nextseqnum+1) % self.K
            # print("TIME:",self.env.now,"RDT_SENDER: rdt_send() called for nextseqnum=",self.nextseqnum," outside the current window. Refusing data.")			
			return False
			# return True

	def rdt_rcv(self,packt):
		# This function is called by the lower-layer 
		# when an ACK packet arrives
		if (packt.corrupted==False):
			# mark the packet as acked
            # check if we got an ACK for a packet within the current window.
			if (packt.seq_num in self.sndpkt.keys()):
				self.acked[packt.seq_num]=True
				# self.acked.append(packt.seq_num)
				# check if the acked packet is the base
				if (packt.seq_num==self.base):
					# find the next base
					while(self.base in self.acked.keys()):
						# self.acked.remove(self.base)
						del self.acked[self.base]
						# print(1)

						del self.sndpkt[self.base]
						self.stop_timer(self.base)
						# delete from the buffer
						
						self.base = (self.base+1) % self.K
					
				# else:
				# 	# stop the timer for recived packet
				# 	self.stop_timer(packt.seq_num)
	
	def timer_behavior(self, seq_num):
		try:
			# Wait for timeout 
			self.timer_is_running[seq_num]=True
			yield self.env.timeout(self.timeout_value)
			self.timer_is_running[seq_num]=False
			# take some actions 
			self.timeout_action(seq_num)
		except simpy.Interrupt:
			# stop the timer
			self.timer_is_running[seq_num]=False

	
	def start_timer(self, seq_num):
		# self.timer = self.env.process(self.timer_behavior())
		# print("TIME:", self.env.now, "TIMER STARTED for a timeout of ", self.timeout_value)
		# print("start timer called", seq_num)
		self.timer[seq_num] = self.env.process(self.timer_behavior(seq_num))
		# print(self.timer[seq_num])
		print("TIME:", self.env.now, "TIMER STARTED for a timeout of ", self.timeout_value, "for the packet", seq_num)

	def stop_timer(self, seq_num):
		# print("TIME:", self.env.now, "TIMER STOPPED")
		# print("stop timer called", seq_num)
		assert(self.timer_is_running[seq_num]==True)
		# print(self.timer[seq_num])
		self.timer[seq_num].interrupt()
		print("TIME:", self.env.now, "TIMER STOPPED for the  packet ", seq_num)

		

	# # Actions to be performed upon timeout
	def timeout_action(self, seq_num):
		# print(2)
		self.channel.udt_send(self.sndpkt[seq_num])
		print("TIME:",self.env.now,"RDT_SENDER: TIMEOUT OCCURED. Re-transmitting the packet",seq_num)
		#increment total packets send and retransmission
		self.num_retransmissions += 1
		self.total_packets_sent += 2
		self.total_packets_sent -= 1
		#start timer for each packet
		# print(3)
		self.start_timer(seq_num)

	# A function to print the current window position for the sender.
	def print_status(self):
		print("TIME:",self.env.now,"Current window:", [(self.base+i)%self.K for i in range(0,self.N)],"base =",self.base,"nextseqnum =",self.nextseqnum)
		print("---------------------")


#==========================================================================================
#==========================================================================================
#==========================================================================================
class rdt_Receiver(object):
	
	def __init__(self,env):
		
		# Initialize variables
		self.env=env 
		self.receiving_app=None
		self.channel=None

		# some default parameter values
		self.ack_packet_length=10 # bits
		self.K = 5 # range of sequence numbers expected
		self.N = 16  # Receiver's Window size

		#initialize state variables
		# self.expectedseqnum=1
		# self.sndpkt= Packet(seq_num=0, payload="ACK",packet_length=self.ack_packet_length)
		
		self.Packets_buffered= {} # a Packets_buffered for storing the packets to be sent (implemented as a Python dictionary)
		
		self.total_packets_sent=0
		self.num_retransmissions=0
	
		self.base=1 # base of the current window 
		self.count=0
 
		

		

	def rdt_rcv(self,packt):
		# If the received packet has already been delivered to the application layer, send an ACK
		if ((not(packt.corrupted)==True )and packt.seq_num in [(self.base-self.N + i)%self.K for i in range(0,self.N)]):
			# this is for debugging 
			# print(4)
			self.num_retransmissions+=1
			self.total_packets_sent+=1
			#print("Time:",self.env.now)
			print("TIME:",self.env.now,"RDT_RECEIVER: rdt_rcv() called for seq_num=",packt.seq_num," already delivered to app. Still Sending ACK.")
			Packet_for_sending= Packet(seq_num=packt.seq_num, payload="ACK", packet_length=self.ack_packet_length)
			self.channel.udt_send(Packet_for_sending)
		
		# Check if the received packet is not corrupted and Check if the received packet sequence number is within the current window
		if ((not(packt.corrupted)==True ) and packt.seq_num in [(self.base+i)%self.K for i in range(0,self.N)]):
			# Packets_buffered the received packet
			self.Packets_buffered[packt.seq_num]=packt
			# Print a message indicating that the packet is received within the current window and sending an ACK
			print("TIME:",self.env.now,"RDT_RECEIVER: rdt_rcv() called for seq_num=",packt.seq_num," within current window. Sending ACK.")
			# this is for debugging 
			# Create an ACK packet to send back to the sender
			Packet_for_sending= Packet(seq_num=packt.seq_num, payload="ACK", packet_length=self.ack_packet_length)
			# Send the ACK packet to the sender
			#print("Time:",self.env.now)
			self.channel.udt_send(Packet_for_sending)
			# Increment the total number of packets sent
			# print(5)
			self.total_packets_sent+=2
			self.total_packets_sent-=1
			#=====================================================================================================
			print("\nTIME:",self.env.now,"RDT_RECEIVER: Currently Packets_buffereded packets:")
			for key_pair in self.Packets_buffered:
				print("TIME:",self.env.now,"RDT_RECEIVER: Packet with seq_num=",key_pair," and payload=",self.Packets_buffered[key_pair].payload)
			print('\n')
			# Print a message indicating the currently Packets_buffereded packets
			# this is for debugging 	
			# Check if the received packet is the base of the current window
			if (self.base==packt.seq_num ):
				print('base is', self.base)
			    # this is for debugging 
				# Deliver all the Packets_buffereded packets that are in order to the application layer
				while self.base in self.Packets_buffered.keys():
					application_layer_message=self.Packets_buffered[self.base].payload
					#print("Time:",self.env.now)
					self.receiving_app.deliver_data(application_layer_message)
					self.total_packets_sent+=1
					self.total_packets_sent-=1 
					# remove the packet from packet_buffered as we have deleivered it to the upper layer
					del self.Packets_buffered[self.base]
					# Increse base or change base 
					self.base = (self.base+1)%self.K
					
	# else we dont have to do anything ,if packet is corrupted simply discard it wait for retransmission 

			