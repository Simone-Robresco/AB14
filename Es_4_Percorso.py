from Alphabot import AlphaBot
import time

robot = AlphaBot()

# modifica velocita'  di default per le ruote per risolvere il problema delle ruote storte
robot.setPWMA(41) # ruota sinistra
robot.setPWMB(39) # ruota destra

# va avanti fino a superare l'ostacolo
robot.forward()
time.sleep(6)

robot.stop()
time.sleep(0.5)

# gira a sinistra perpendicolarmente alla traccia precedente
robot.left()
time.sleep(0.5)

robot.stop()
time.sleep(0.5)

# va avanti un po' per superare l'ostacolo
robot.forward()
time.sleep(1)

robot.stop()
time.sleep(0.5)

# gira a sinistra per poter arrivare a destinazione
robot.left()
time.sleep(0.5)

robot.stop()
time.sleep(0.5)

# modifica della velocita'  delle ruote nel caso in cui si siano svitate un po' nel pezzo precedente
robot.setPWMA(42)
robot.setPWMB(41)

# va avanti fino alla fine
robot.forward()
time.sleep(6.5)
