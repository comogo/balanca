#!/usr/bin/env python
# *-* coding: utf-8 -*-
import ConfigParser
import serial
import time
import os


class Balanca(object):
    """
    Classe que representa a balança.
    """

    CONFIG_FILENAME = 'config.cfg'

    def __init__(self, port=0, baudrate=9600, parity='N', bytesize=8, stopbits=1, timeout=0, output_filename='/home/balanca/peso.txt'):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.timeout = timeout
        self.output_filename = output_filename

        self.regex = ''
        self.debug = False
        self.tipo_balanca = 'b1'

        self.connection = None
        self.previous_data  = ''
        self.actual_data = ''

    def load_config(self, filename=None):
        """
        Lê as configurações do arquivo.
        """
        if filename is None:
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.CONFIG_FILENAME)

        config = ConfigParser.ConfigParser()
        config.read(filename)

        self.port = config.get('connection', 'port', '0')
        self.baudrate = int(config.get('connection', 'baudrate', '9600'))
        self.parity   = config.get('connection', 'parity', 'N')
        self.bytesize = int(config.get('connection', 'bytesize', '8'))
        self;stopbits = int(config.get('connection', 'stopbits', '1'))
        self.timeout  = float(config.get('connection', 'timeout', '1'))
        self.output_filename = config.get('out', 'file', self.output_filename)
        self.debug = config.get('misc', 'debug', '0') != '0'
        self.tipo_balanca = config.get('misc', 'tipo_balanca', 'b1')
        self.regex = config.get('regex', self.tipo_balanca, '" \d+ "')[1:-1]

    def __write_data(self, data):
        """
        Escreve os dados no arquivo de saída.
        """
        data.strip()
        f = open(self.output_filename, 'w')
        f.write(data)
        f.close()
        if self.debug:
            print "Escrevendo >> ", data

    def __read_raw_data(self):
        """
        Lê dados da balança.
        """
        read = self.connection.read(500)
        if self.debug:
            print "Lendo      >> ", read
        return read

    def __open_connection(self):
        """
        Abre uma conexão com a porta serial.
        """
        ok = False
        while not ok:
            try:
                self.connection = serial.Serial(port=self.port, baudrate=self.baudrate,
                                stopbits=self.stopbits, parity=self.parity,
                                bytesize=self.bytesize, timeout=self.timeout)
                ok = True
            except:
                self.connection.close()

    def __close_connection(self):
        """
        Fecha a conexão com a porta serial.
        """
        self.connection.close()

    def __reset_connection(self):
        self.__close_connection()
        self.__open_connection()

    def __get_data(self, data):
        """
        Transforma a entrada raw em valor.
        Caso não haja dados retorna None.
        """
        from re import findall

        matches = findall(self.regex, data)
        if len(matches) > 0:
            return matches[-1].strip()
        return None


    def run_forever(self, sleep_time=0.2):
        """
        Função princioal
        """
        self.__open_connection()
        while True:
            try:
                raw_data = self.__read_raw_data()
                data = self.__get_data(raw_data)
                if data:
                    self.actual_data = data
                    if self.actual_data != self.previous_data:
                        self.__write_data(self.actual_data)
                        self.previous_data = self.actual_data
                else:
                    self.__write_data('')
                    self.actual_data = ''
                    self.previous_data = ''
            except Exception,e:
                self.__write_data('')
                self.actual_data = ''
                self.previous_data = ''
                self.__reset_connection()

            time.sleep(sleep_time)

if __name__=="__main__":
    balanca = Balanca()
    balanca.load_config()
    balanca.run_forever()

