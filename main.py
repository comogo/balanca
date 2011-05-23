# *-* coding: utf-8 -*-
import ConfigParser
import serial
import time
import re
import os

CONFIG_DEFAULT = 'config.cfg'

def ler_configs(filename=CONFIG_DEFAULT):
    """
    Lê as configurações do arquivo.
    """
    config = ConfigParser.ConfigParser()
    config.read(filename)
    conf = {
        'port':     config.get('connection', 'port', '0'),
        'baudrate': int(config.get('connection', 'baudrate', '9600')),
        'parity':   config.get('connection', 'parity', 'N'),
        'bytesize': int(config.get('connection', 'bytesize', '8')),
        'stopbits': int(config.get('connection', 'stopbits', '1')),
        'timeout': float(config.get('connection', 'timeout', '1')),
    }
    saida = config.get('out', 'file', '/home/balanca/peso.txt')
    return (conf, saida,)

def gravar_valor(filename, valor):
    f = open(filename, 'w')
    f.write(valor)
    f.close()

if __name__=="__main__":
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_DEFAULT)
    config, filename = ler_configs(filename)
    valor_anterior = ''
    valor_atual = ''
    while True:
        try:
            ser = serial.Serial(**config)
            leitura = ser.read(500)
            matches = re.findall(' \d+ ', leitura)
            if len(matches) > 0:
                valor_atual = matches[-1].strip()
                if valor_atual != valor_anterior:
                    gravar_valor(filename, valor_atual)
                    valor_anterior = valor_atual
            else:
                gravar_valor(filename, '')
                valor_anterior = ''
                valor_atual = ''
                
        except Exception,e:
            gravar_valor(filename, '')
            valor_anterior = ''
            valor_atual = ''
            ser.close()
            ser = serial.Serial(**config)
        time.sleep(0.2)
