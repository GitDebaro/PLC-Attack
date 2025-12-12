# Ataques a PLCs

## Ejercicio 1

Ejecutamos el contenedor con el simulador del entorno SCADA:
```
rocker --x11 --network host --privilege --name cifi-modbus claudiaalvarezaparicio/cifi-modbus:latest
```
En esta sección buscamos averiguar cierta información sobre el funcionamiento del protocolo Modbus y la interacción entre las distintas partes del sistema SCADA:
* Simulador de planta industrial
* PLC que trabaja con Modbus/TCP
* HMI utilizada para controlar el funcionamiento de la planta

Para esta sección de la práctica se han seguido los siguientes pasos:

1. Iniciamos **wireshark**, incluido en el contenedor de Docker, para capturar los paquetes Modbus intercambiados.
```
wireshark
```
2. Encendemos el sistema de la planta haciendo click en el botón **RUN**.
3. A continuación, detenemos la captura del wireshark para poder analizar los paquetes capturados. El sistema quedará encendido. Podemos ver dos tipos de paquetes que se repiten constantemente y que tienen asociados las siguientes etiquetas:
    * Write Single Coil
    * Read Coils

IMG1

La gran mayoría de paquetes tienen el campo Data a 0, por lo que destacan una decena de paquetes que mandan 'ff00' al sistema.

IMG2

En esta última imagen se puede observar que la función de escritura (Write Single Coil) tiene asociado el código 5 dentro de Modbus, mientras que la función de lectura (Read Coils) recibe el código 1; como se puede ver en la siguiente imagen:

IMG3

4. Siguiendo con la captura de la ejecución, se observa que cada vez que la caja entra el rango del robot se realizan dos Queries con los Reference Numbers 3 y 4, probablemente asociados a las secciones del PLC que detectan que la caja está en el rango efectivo del robot y activan a este último.

IMG4

5. Finalmente, se procede a apagar el sistema. Todos los paquetes de escritura capturados contienen el campo Data a 0, por lo que se supone que este valor es el utilizado para apagar las funciones del sistema; y que hay pocos paquetes enviados con Reference Numbers 1 y 2 (entre los que se encuentran las respuestas a estos paquetes).

IMG5

### ¿Cuál es el código de función para modificar un valor?
Como hemos visto gracias a la captura de paquetes en Wireshark, el código de la función de escritura es 5.

### ¿Cuál es el código de función para leer un valor?
Obtenido de la misma forma que en el caso anterior, el código de la función de lectura es 1.

### ¿Cuál es el tipo de dato que se lee o se escribe?
Para esta pregunta se han revisado en fuentes públicas los distintos tipos de datos con los que trabaja Modbus. Uno de ellos nos es bastante familiar ya que lo hemos visto en las funciones mencionadas anteriormente, Coils; registros de 1 bit que concuerdan con los cuatro bits encontrados en la IMG3.
https://help.campbellsci.com/CR6/Content/shared/Communication/Modbus/modbus-infostorage.htm?TocPath=Communications%20protocols%7CModbus%20communications%7C_____7 

## Ejercicio 2

Para esta parte de la práctica vamos a utilizar el modulo ```pymodbus``` de Python. En concreto, el script asociado ha sido desarrollado en la versión 3.12.3 de Python. El bloque principal de código inicia la conexión sobre localhost hacia el puerto 502, el asignado por defecto al protocolo Modbus. En caso de error, el script finaliza; en caso contrario, entramos en la función menú, en la que podemos elegir el tipo de ataque a realzar. Finalmente, cierra el socket asociado a la conexión.
```
client = ModbusTcpClient("127.0.0.1",port=502)
if not client.connect():
    print("Connection error")
    exit()
    
print("Connection succesfull")
menu()
client.close()
```

La función menú muestra los ataques disponibles gracias a la opción match, análoga a la sentencia switch case que está disponible desde Python 3.10 y posteriores.

### Move on
Una vez creada la conexión se trata de utilizar las funciones asociadas a la lectura y escritura de coils de la planta. Comenzamos por la función de escritura ya que es clave para realizar estos ataques. El primer argumento es el offset dentro de la estructura del PLC del componente de la planta, en nuestro caso: el componente RUN, el robot y la cinta mecánica. El segundo argumento es el valor a escribir, True para encendido y False para apagado. El último es el identificador entero de la unidad Modbus, nuestro PLC.
```
client.write_coil(offset del componente del PLC, Bool (True/False), unit=int)
```
Debemos obtener el offset de los distintos componentes para realizar el ataque. Para ello, vamos probando distintos offsets uno a uno hasta tener el siguiente listado:
```
RUN_CODE = 0
ROBOT_CODE = 1
CONVEYOR_CODE = 2
```
Una vez obtenida esta información, mediante un bucle while leemos constantemente los valores de los coils de dichos componentes y en caso de que alguno este apagado, sobrescribimos su valor para encenderlo. El código actual lo revisa de forma constante para evitar que pulsaciones repetidas consigan apagar el sistema, si no se considera práctico u óptimo, valdría colocar un sleep() para retrasar las comprobaciones.

### Stop all
Este ataque es justo el opuesto al anterior, en caso de que haya algún componente encendido, se sobrescribe el valor del coil a 0 para apagarlo.

### Stop robot
De manera similar al segundo ataque, si el coil del robot está a 1, se cambia su valor a 0. Es básicamente la misma funcionalidad pero afectando solo al componente del PLC que controla el robot.