import furnace
import sys

furnace = furnace.Furnace('127.0.0.1', 3050, sys.argv[1])
furnace.connect()
while True:
    furnace.clear_setting()
    furnace.RecvStartOrder()
    furnace.FurnaceMain()

furnace.close()