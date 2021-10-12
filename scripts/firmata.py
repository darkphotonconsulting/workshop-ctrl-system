from pyfirmata import util, ArduinoMega
import platformio



board = ArduinoMega('/dev/ttyACM0')


print(board.digital)

for pin in board.digital:
    print(dir(pin))
    print(pin.mode)
    print(pin.pin_number)
    print(pin.value)



#print(board.firmware)


print(util.pin_list_to_board_dict(
  board.digital  
))