# Imperialism remake
# Copyright (C) 2014 Trilarion
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import json, zlib, random
from functools import partial

from PySide import QtCore, QtNetwork

def serialize_compress_and_write_to_socket(socket, value):
    """

    """
    # serialize value to json
    serialized = json.dumps(value, indent=0)

    # encode to utf-8 bytes and compress
    compressed = zlib.compress(serialized.encode())

    # wrap in QByteArray
    bytearray = QtCore.QByteArray(compressed)

    # write using a data stream
    writer = QtCore.QDataStream(socket)
    writer.setVersion(QtCore.QDataStream.Qt_4_8)
    writer << bytearray

def read_from_socket_uncompress_and_deserialize(socket):
    """

    """
    # read a QByteArray using a data stream
    reader = QtCore.QDataStream(socket)
    bytearray = QtCore.QByteArray()
    reader >> bytearray

    # uncompress bytes from bytearray
    uncompressed = zlib.decompress(bytearray.data())

    # decode from utf-8 bytes to unicode and deserialize from json
    deserialized = json.loads(uncompressed.decode())

    return deserialized

SCOPE = {
    'local': QtNetwork.QHostAddress.LocalHost,
    'any': QtNetwork.QHostAddress.Any
}

class EnhancedSocket(QtCore.QObject):

    received = QtCore.Signal(dict)

    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.socket.readyRead.connect(self.receive)
        self.socket.error.connect(self.error)
        print('new connection id {}, address {}, port {}'.format(id, socket.peerAddress().toString(), socket.peerPort()))

    def receive(self):
        while self.socket.bytesAvailable() > 0:
            value = read_from_socket_uncompress_and_deserialize(self.socket)
            print('connection id {} received {}'.format(self.id, json.dumps(value)))
            self.received.emit(value)

    def error(self):
        self.socket.disconnectFromHost()

    def send(self, value):
        """
            We send a message back to the client.
        """
        serialize_compress_and_write_to_socket(self.socket, value)


class Server(QtCore.QObject):
    """
        Wrapper around QtNetwork.QTcpServer and a management of several clients (each a QtNetwork.QTcpSocket).
    """

    new_client = QtCore.Signal(EnhancedSocket)

    def __init__(self, EnhancedSocketClass):
        """
        """
        super().__init__()
        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.new_connection)
        self.clients = []
        self.EnhancedSocketClass = EnhancedSocketClass

    def start(self, port, scope='local'):
        """
            Given an address (hostname, port) tries to start listening.
            QtNetwork.QHostAddress.Any
        """
        host = SCOPE[scope]
        if not self.server.listen(host, port):
            raise RuntimeError('Network error: cannot listen')

    def isListening(self):
        return self.server.isListening()

    def scope(self):
        if self.isListening():
            return SCOPE.keys()[SCOPE.values().index(self.server.serverAddress())]
        else:
            return None

    def stop(self):
        """
            Stopps listening.
        """
        if self.isListening():
            self.server.close()

    def new_connection(self):
        """
            Zero or more new clients might be available, give them an id and wire them.
        """
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection() # returns a QTcpSocket
            # create new client
            client = self.EnhancedSocketClass(socket)
            # add to client list
            self.clients.extend([client])
            # add disconnected signal to remove client
            socket.disconnected.connect(partial(self.disconnected, client))

    def disconnected(self, client):
        """
            One connection disconnected. Remove from list
        """
        self.clients.remove(client)
