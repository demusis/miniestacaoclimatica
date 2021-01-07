# Programa de dataloogger com Cayenne
# Autor: Carlo Ralph De Musis
# Data: junho/2018

# Comunicacao com o Cayenne
# pip3 install cayenne-mqtt

# Data Logger
import cayenne.client 
import time, sys, csv
from sense_hat import *
import numpy as np
import RPi.GPIO as GPIO

# --------------------------

# Informações de autenticação obtidas no dashboard da Cayenne.
MQTT_USERNAME  = "d8c8efc0-806c-11e7-88a0-c7ea1897b6ae"
MQTT_PASSWORD  = "da6aac1d087b3a403c48b5c5125604a4c1457851"
MQTT_CLIENT_ID = "de20f590-8885-11e8-b98d-6b2426cc1856"

# Retorno do recebimento de mensagem pela Cayenne.
def on_message(message):
  print("Mensagem recebida: " + str(message))
  # Caso ocorra erro de processamento retorne string.

client = cayenne.client.CayenneMQTTClient()
client.on_message = on_message
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID)

# --------------------------

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

sh = SenseHat()
sh.clear()

tempo_leituras = 10 # Segundos

while True:
  try:
      time.sleep(tempo_leituras) 
      
      client.loop()
      
      tFile = open('/sys/class/thermal/thermal_zone0/temp')
      temp = float(tFile.read())
      t_CPU = temp/1000
      #GPIO.output(17, 1)
      
      t_SH = sh.get_temperature()
      t_SH_H = sh.get_temperature_from_humidity()
      t_SH_P = sh.get_temperature_from_pressure()
      P = sh.get_pressure()
      UR = sh.get_humidity()

      client.celsiusWrite(0, t_SH)
      client.celsiusWrite(1, t_SH_H)
      # client.celsiusWrite(2, t_SH_P)
      client.virtualWrite(2, t_SH_P, "temp", "c")
      
      client.virtualWrite(3, P, "bp", "pa")
      client.virtualWrite(4, UR, "rel_hum", "p")
      
      client.celsiusWrite(5, t_CPU)

      sh.show_message('%.1fC' % t_CPU, text_colour=[255, 0, 0])    # Temperaturada CPU
      sh.show_message('%.1fC' % t_SH, text_colour=[0, 255, 0])     # Temperatura do Sense Hat
      sh.show_message('%.1fpa' % P, text_colour=[130, 130, 130])   # Pressão atmosférica
      sh.show_message('%.1f%%' % UR, text_colour=[0, 0, 255])      # Umidade relativa
      
      print(time.strftime("%d-%m-%Y %H:%M:%S"),',', t_CPU,',', t_SH,',', P,',',UR)
  
      # t_CPU, t, t_h, t_p, UR, P
      registro = [time.strftime("%d-%m-%Y %H:%M:%S"), t_CPU, t_SH, t_SH_H, t_SH_P, P, UR]    
      with open('templog.csv', 'a') as f:
           w = csv.writer(f)
           w.writerow(registro)          
          
  except:
      tFile.close()
      #GPIO.cleanup()
      f.close()
      exit
    