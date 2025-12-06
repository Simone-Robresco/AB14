from Alphabot import AlphaBot
import RPi.GPIO as GPIO
import time

robot = AlphaBot()

# setup dei pin dei sensori in input
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.IN) # sensore sinistro
GPIO.setup(16, GPIO.IN) # sensore destro

# modifica velocitÃ  delle ruote per risolvere il problema delle ruote storte
robot.setPWMA(31) # ruota sinistra
robot.setPWMB(30) # ruota destra


while True:
	robot.forward()
	time.sleep(0.05)
	
	# funzione per rilevare un ostacolo a sinistra
	if GPIO.input(19) == 0:
		print ('ostacolo SX')
		robot.stop()
		time.sleep(0.5)
		robot.backward()
		time.sleep(0.5)
		robot.right()
		time.sleep(0.5)

	# funzione per rilevare un ostacolo a destra
	if GPIO.input(16) == 0:
		print ('ostacolo DX')
		robot.stop()
		time.sleep(0.5)
		robot.backward()
		time.sleep(0.5)
		robot.left()
		time.sleep(0.5)

	# funzione per rilevare un ostacolo davanti
	if GPIO.input(19)== 0 and GPIO.input(16) == 0:
		print ('ostacolo davanti')
		robot.stop()
		time.sleep(0.5)
		robot.backward()
		time.sleep(0.5)
		robot.right()
		time.sleep(0.5)
