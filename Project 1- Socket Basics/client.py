#!/usr/bin/env python3

# Sahil Sah
# CS5700 - Networking Fundamentals
# Project 1: Simple Client
# Spring 2023


"""
This assignment was to learn the basics of network coding and communicate with a server
using sockets. It solves hundreds of complex math expression and if completed successfully,
will return a secret flag back. 
"""
import socket
import ssl
import argparse

"""
HELLO message to server format: cs5700spring2023 HELLO [your Northeastern-username]\n
EVAL message format: cs5700spring2023 EVAL [txpr]\n
STATUS message format: cs5700spring2023 STATUS [solution]\n
ERR format: cs5700spring2023 ERR [emsg]\n
BYE format: cs5700spring2023 BYE [a 64 byte secret flag]\n
"""

# Global constants for message fields client may use or messages 
# recieved/sent to the socket

HELLO = 'HELLO'
EVAL = 'EVAL'
STATUS = 'STATUS'
ERR = 'ERR'
BYE = 'BYE'

COURSE = 'cs5700spring2023'
MSG_BUFFER = 16384
SOCKET_PORT = 27995
FORMAT = 'utf-8'
DIVISION_ERR = '#DIV/0'

#
# Helper function to recieve the message from the server
# 
# @param = socket
# returns message back from socket
#
def receiveMessage(socket):
    return(socket.recv(MSG_BUFFER).decode(FORMAT))

#
# Helper function to send the hello message to the server
# 
# @param = username
# @param = socket
# returns None
#
def sendHello(username, socket):
    try:
        hello = COURSE + " " + HELLO + " " + username + "\n"
        socket.send(hello.encode(FORMAT))
    except Exception as error:
        print(error)
        print("There was an error sending the message to the socket")
        return
#
# Helper function to get all the command line arguments from user
# 
# @param none
# returns associated arguments to be called in main
#
def readCommandInput():
    parser = argparse.ArgumentParser()
    #Adding port number in the statement is optional but -s is required
    parser.add_argument('-s', action='store_true', required= True, help='The client should use an encrypted socket connection')
    parser.add_argument('-p', '--port', type=int, default=27995, help='Server port; Defaults to 27995')
    parser.add_argument('host',type=str, help='hostname')
    parser.add_argument('username', type=str, help='username')

    requiredArguments = parser.parse_args()
    
    return(requiredArguments.host, requiredArguments.port, requiredArguments.username)
#
# Math calculations are being done via shunting yard algorithm
# This function will read the expression and conduct the math based on
# assignments in dictionary.
# 
# @param = item1
# @param = item2
# @param = operator
# returns back 
#  
def readExpression(item1, item2, operator):
    isFlag = False
    evaluationResult = 0
    operations = {'+': lambda x, y: x+y, '-': lambda x, y: x-y, '*':
     lambda x, y: x*y, '//': lambda x, y: x//y, 
     '<<^': lambda x, y: (x << 13)^y}
    try:
        evaluationResult = operations[operator](item1, item2)
    except:
        isFlag = True
    return evaluationResult, isFlag

#
#Loop over the elements in the expression and check if it is a valid operator
#as well as determine precedence. If there is '(' then it gets added into the operatorStack
# and if there is ')' we need to validate there is the correct amount of parentheses for a valid
#math expression and if its a operator in the list below then append to operand
# 
# @param = tree_expression
# returns back False (for readExpression) and integer
#       
def evaluation(tree_expression):
    operandStack = []
    operatorStack = []
    for item in tree_expression:
        if item in ('(', '+', '-', '*', '//', '<<^'):
            operatorStack.append(item)
        elif item == ')':
            while operatorStack and operatorStack[-1] != '(':
                item2, item1 = operandStack.pop(), operandStack.pop()
                operator = operatorStack.pop()
                solution, hasError = readExpression(item1, item2, operator)
                if hasError: return solution, hasError
                operandStack.append(solution)
                operatorStack.pop()
        elif item.lstrip('-').isdigit():
            operandStack.append(int(item))
    return operandStack[-1], False

#
# Helper function to read the message being recieved and handle it based on
# what is contained in the message so validity is checked
# 
# @param = message
# @param = flag
# returns back EVAL or BYE after split back from the message
#  
def checkMessage(message, flag):
    if not message or not flag:
        return False
    splitMessage = message.split()
    if len(splitMessage) < 2 or splitMessage[0] != COURSE:
        return False
    return splitMessage[1] in (EVAL, BYE) if flag == EVAL else \
    splitMessage[1] == BYE

def main(host, port, username):
    try:
        #Create socket connection and wrap it in SSL format
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSSL = ssl.wrap_socket(clientSocket, ssl_version=ssl.PROTOCOL_SSLv23)
        address = host, port
        clientSSL.connect(address)
    except Exception as error:
        print(error)
        print("Error: Socket connection failed!")
    
    #Sending hello to server via function
    sendHello(username, clientSSL)

    #Recieve the return message and begin parsing through the statement and math expression
    parseMessage = receiveMessage(clientSSL)
    try:
        #If message contains EVAL then read math expression and conduct operations
        while ((EVAL in parseMessage) and checkMessage(parseMessage, EVAL)):
            message = parseMessage.split()
            split = message[2:]
            isFlag = False
            solution, isFlag = evaluation(split)
            # If there is division error send back error
            if isFlag:
                errorMessage = COURSE + " " + ERR + " " + DIVISION_ERR+ "\n"
                clientSSL.send(errorMessage.encode(FORMAT))
                isFlag = False
            #Send evaluation result back
            else:
                status = COURSE + " " + STATUS + " " + str(solution) + "\n"
                clientSSL.send(status.encode(FORMAT))

            parseMessage = receiveMessage(clientSSL)

        #If message sent back contains bye then split up the message and just print secret flag
        if ((BYE in parseMessage) and checkMessage(parseMessage, BYE)):
            secretFlag = parseMessage.split()
            secretFlag = secretFlag[2:]
            string = "".join(secretFlag)
            print(string)
            clientSSL.close()
    # If math operations are not being solved correctly by algorithim then put out error
    # so its known algorithim is not correct
    except Exception as error:
        print(error)
        print("The math expression was not solved correctly!")
        clientSSL.close()
    

if __name__ == "__main__":
    host, port, username = readCommandInput()
    main(host, port, username)
