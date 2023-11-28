import pygame
import random
import sys
import logging

# Configuración del registro
logging.basicConfig(filename='simulador_ecosistema.log', level=logging.INFO)


# Configuración inicial de Pygame
pygame.init()
ANCHO = 1200
ALTO = 750
ventana = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()
# Bucle principal del juego que se ejecuta continuamente
logging.info("Inicio de la simulacion")

class Cadaver:
    def __init__(self, x, y especie, color):
        self.x = x
        self.y = y
        self.especie = especie
        self.color = color

class Organismo:
    def __init__(self, x, y, vida, energia, velocidad):
        self.x = x
        self.y = y
        self.vida = vida
        self.energia = energia
        self.velocidad = velocidad
        self.razon_muerte = None  # Agregar la variable de razón de muerte

    def perder_energia(self):
        # Los organismos pierden energía en cada ciclo
        self.energia -= 1
        if self.energia <= 0:
            self.vida = 0  # El organismo muere si se queda sin energía
            self.razon_muerte = "Agotamiento de energía"

    def mover(self):
        # Movimiento aleatorio sin salir de la pantalla
        desplazamiento_x = random.randint(-1, 1)
        desplazamiento_y = random.randint(-1, 1)

        nueva_posicion = (
            (self.x + desplazamiento_x * self.velocidad) % ANCHO,
            (self.y + desplazamiento_y * self.velocidad) % ALTO
        )
        self.x, self.y = nueva_posicion
        self.perder_energia()

        # Verificar si el organismo ha muerto después de perder energía
        if self.vida <= 0:
            self.morir("Agotamiento de energía")

    def morir(self, razon):
        mensaje= f"El organismo ha muerto por {razon}."
        print(mensaje)
        logging.info(mensaje)


class Animal(Organismo):
    def __init__(self, x, y, vida, energia, velocidad, especie, dieta, genero):
        super().__init__(x, y, vida, energia, velocidad)
        self.especie = especie
        self.dieta = dieta
        self.genero = genero
        self.hidratacion = 100  # Nueva variable de hidratación
        self.razon_muerte = None  # Inicializar la razón de muerte
        self.cadaver = None

    def morir(self):
        # Lógica para cuando el animal muere
        self.cadaver = Cadaver(self.x, self.y)
    def perder_energia(self):
        # Pérdida de energía adicional para animales
        super().perder_energia()
        if self.vida > 0:  # Verificar si el animal todavía está vivo
            self.energia -= 0.5  # Ajusta la cantidad de pérdida de energía según tus necesidades
            if self.energia <= 0:
                self.vida = 0
                self.razon_muerte = "Agotamiento de energía"
                self.morir(self.razon_muerte)  # Llamar a la función morir con la razón de muerte

    def beber_agua(self, ambiente):
        # Verificar si el animal está cerca del agua (en las orillas del lago)
        distancia_agua = abs(self.x - ambiente.posicion_lago[0]) + abs(self.y - ambiente.posicion_lago[1])
        if distancia_agua <= 50 and self.y > ambiente.posicion_lago[1] - 5:  # Ajusta el valor según la distancia y posición que consideres apropiadas
            self.hidratacion = min(100, self.hidratacion + 10)  # Aumentar la hidratación, pero no más allá de 100
            mensaje=f"El {self.especie} está bebiendo agua en ({self.x}, {self.y}). Hidratación: {self.hidratacion}"
            print(mensaje)
            logging.info(mensaje)
            # Verificar si el organismo está cerca del agua
        for charco in ambiente.charcos.copy():
            distancia_x = abs(self.x - charco[0])
            distancia_y = abs(self.y - charco[1])
            if distancia_x <= 20 and distancia_y <= 20:
                # Eliminar el charco si el animal está en un charco
                ambiente.charcos.remove(charco)
                self.hidratacion = min(100, self.hidratacion + 10)
                mensaje=f"El {self.especie} ha bebido del charco en ({charco[0]}, {charco[1]}).Hidratación: {self.hidratacion}"
                print(mensaje)
                logging.info(mensaje)
                return
        # Reducir la hidratación si no hay charco cercano
        self.hidratacion -= 1

    def mover(self):
        # Movimiento modificado para afectar la hidratación
        super().mover()
        self.hidratacion -= 0.5  # la hidratación disminuye al moverse

        # Verificar si el organismo está en el suelo desértico y reducir la hidratación más rápidamente
        if ambiente.suelo_desertico.colliderect(pygame.Rect(self.x, self.y, 1, 1)):
            self.hidratacion -= 3  # Ajusta la velocidad de deshidratación en el desierto según tus necesidades

            # Verificar si el organismo ha muerto por deshidratación
            if self.hidratacion <= 0:
                self.vida = 0
                self.razon_muerte = "Deshidratacion"
                self.morir(self.razon_muerte)

    def cazar(self, presa):
    # Lógica de caza
        distancia_x = abs(self.x - presa.x)
        distancia_y = abs(self.y - presa.y)

        if distancia_x <= 10 and distancia_y <= 10:
            self.energia += 20
            mensaje=f"¡El {self.especie} cazó a otro animal en ({presa.x}, {presa.y})"
            print(mensaje)
            logging.info(mensaje)
            presa.vida = 0
            presa.razon_muerte = f"Cazado por un {self.especie}"  # Corregir la interpolación de cadena

    def reproducirse(self, otro_animal):
        # Lógica de reproducción
        distancia_x = abs(self.x - otro_animal.x)
        distancia_y = abs(self.y - otro_animal.y)

        probabilidad_reproduccion = 0.9 # Ajusta este valor según tus preferencias

        if (
            self.energia > 50
            and self != otro_animal
            and isinstance(otro_animal, Animal) and otro_animal.especie == self.especie
            and distancia_x <= 10
            and distancia_y <= 10
            and self.genero != otro_animal.genero
            and random.random() < probabilidad_reproduccion
        ):
            # Crear un nuevo animal solo si están lo suficientemente cerca, son de la misma especie,
            # de géneros opuestos y hay probabilidad de reproducción
            nueva_posicion = (
                (self.x + random.randint(-20, 20)) % ANCHO,
                (self.y + random.randint(-20, 20)) % ALTO
            )

            nuevo_animal = Animal(
                nueva_posicion[0],
                nueva_posicion[1],
                100,
                50,
                10,
                self.especie,
                self.dieta,
                random.choice(["macho", "hembra"]),
            )
            return nuevo_animal
        return None

    def alimentarse(self, organismo, lista_organismos):
        # Lógica de alimentación
        if isinstance(organismo, Planta) and organismo.vida > 0 and abs(self.x - organismo.x) <= 20 and abs(self.y - organismo.y) <= 20:
            organismo.vida = 0
            self.energia += 10  # Ganar energía al alimentarse de plantas
            lista_organismos.remove(organismo)   # Eliminar la planta consumida
            mensaje=f"El {self.especie} se alimentó de una planta en ({organismo.x}, {organismo.y}). Energía actual: {self.energia}"
            print(mensaje)
            logging.info(mensaje)
    
    def morir(self, razon):
        if razon == "Deshidratacion":
            mensaje=f"El {self.especie} ha muerto por deshidratación en la posición ({self.x}, {self.y})."
            print(mensaje)
            logging.info(mensaje)
        else:
            mensaje= f"El {self.especie} ha muerto por {razon}."
            print(mensaje)
            logging.info(mensaje)


    def pelear(self, otro_animal):
        # Lógica de la pelea entre dos animales carnívoros
        if (
            isinstance(otro_animal, Animal)
            and self.dieta == "Carnívora"
            and otro_animal.dieta == "Carnívora"
            and self != otro_animal
            and self.x == otro_animal.x
            and self.y == otro_animal.y
        ):  
            mensaje=f"¡{self.especie} y {otro_animal.especie} se encuentran en la misma posición y comienzan a pelear!"
            print(mensaje)
            logging.info(mensaje)
            # El animal con más energia inicial sobrevive
            if self.energia > otro_animal.energia:
                mensaje=f"{self.especie} ha ganado la pelea contra {otro_animal.especie}!"
                print(mensaje)
                logging.info(mensaje)
                self.energia -= otro_animal.energia
                otro_animal.vida = 0
                otro_animal.razon_muerte = f"Derrotado por un {self.especie}"
                otro_animal.morir(otro_animal.razon_muerte)
            elif self.vida < otro_animal.vida:
                mensaje=f"{otro_animal.especie} ha ganado la pelea contra {self.especie}!"
                print(mensaje)
                logging.info(mensaje)
                otro_animal.energia -= self.energia
                self.energia = 0
                self.razon_muerte = f"Derrotado por un {otro_animal.especie}"
                self.morir(self.razon_muerte)
            else:
                mensaje=f"{self.especie} y {otro_animal.especie} empataron en la pelea!"
                print(mensaje)
                logging.info(mensaje)


class Planta(Organismo):
    def __init__(self, x, y, vida, energia):
        super().__init__(x, y, vida, energia, 0)  # Las plantas no se mueven
        self.especie = "Planta"  # Agregar el atributo especie
        self.hidratacion = 100  # Agregar el atributo hidratacion

    def fotosintesis(self):
        # Lógica de fotosíntesis
        self.energia += 3

    def reproducir(self):
        # Lógica de reproducción por semillas
        if random.random() < 0.01:
            nueva_posicion = (
                (self.x + random.randint(-20, 20)) % ANCHO,
                (self.y + random.randint(-20, 20)) % ALTO
            )

            # Verificar que la nueva planta no esté dentro del área del lago
            distancia_lago = abs(nueva_posicion[0] - ambiente.posicion_lago[0]) + abs(nueva_posicion[1] - ambiente.posicion_lago[1])
            if distancia_lago > 30:  # Ajusta el valor según la distancia que consideres apropiada
                nueva_planta = Planta(nueva_posicion[0], nueva_posicion[1], 50, 30)
                mensaje=f"¡Una nueva planta ha crecido en ({nueva_posicion[0]}, {nueva_posicion[1]})"
                print(mensaje)
                logging.info(mensaje)
                return nueva_planta
        return None

    def morir(self, razon):
        mensaje=f"La {self.especie} ha muerto por {razon}."
        print(mensaje)
        logging.info(mensaje)
    


class Ambiente:
    def __init__(self):
        self.factores_abioticos = {
            "temperatura": 25,
            "humedad": 50,
            "viento": 10
        }
        self.ciclos_meteorito = 20
        self.ciclos_tornado = 20
        self.ciclos_transcurridos_meteorito = 0
        self.ciclos_transcurridos_tornado = 0
        self.tornado_activado = False
        self.posicion_tornado = (random.randint(0, ANCHO), random.randint(0, ALTO))
        self.zona_impacto_tornado = set()
        self.tornado_efecto_activado = False
        self.tiempo_restante_tornado = 0
        self.ciclos_lluvia = 10  # Número de ciclos para que ocurra la lluvia
        self.ciclos_transcurridos_lluvia = 0
        self.lluvia_activada = False
        self.charcos = set()  # Conjunto para almacenar la posición de charcos
        self.agua_charco = 30
        # Agregar un cuarto de mapa con suelo desértico
        self.suelo_desertico = pygame.Rect(ANCHO // 2, ALTO // 2, ANCHO // 2, ALTO // 2)
        self.color_desertico = (255, 255, 102)  # Color amarillo
        self.agua = 100  # Inicializar el nivel de agua
        # Posición del lago en el centro del mapa
        self.posicion_lago = (ANCHO // 2, ALTO // 2)

    def dibujar_contador_animales(self, ventana, ecosistema):
        fuente = pygame.font.Font(None, 24)  # Ajusta el tamaño de la fuente según tus preferencias
        texto = fuente.render("Contador de Animales", True, (0, 0, 0))
        ventana.blit(texto, (ANCHO - 200, 10))  # Ajusta las coordenadas de posición según tus preferencias

    # Dibuja el contador para cada especie
        for especie, cantidad in ecosistema.contador_animales.items():
            color = self.obtener_color_animal(especie)
            texto_especie = fuente.render(f"{especie}: {cantidad}", True, color)
            ventana.blit(texto_especie, (ANCHO - 200, 30 + 20 * len(ecosistema.contador_animales) + 20 * list(ecosistema.contador_animales.keys()).index(especie)))

    def obtener_color_animal(self, especie):
        if especie == "Cebra":
            return (128, 255, 255)
        elif especie == "León":
            return (255, 128, 255)
        elif especie == "Tigre":
            return (255, 128, 0)
        elif especie == "Antilope":
                            return (255, 0, 255)
        elif especie == "Yena":
            return (128, 0, 0)
        elif especie == "Jirafa":
            return (255, 255, 0)
        elif especie == "Lobos":
            return (128, 128, 128)
        elif especie == "Bufalo":
            return (128, 255, 0)
        else:
            return (0, 0, 0)
    def aplicar_clima(self, ecosistema):
        self.factores_abioticos["temperatura"] += random.randint(-2, 2)
        self.factores_abioticos["humedad"] += random.randint(-5, 5)
        self.factores_abioticos["viento"] += random.randint(-3, 3)

        if self.ciclos_transcurridos_meteorito % self.ciclos_meteorito == 0 and random.random() < 0.6:
            self.impacto_meteorito(ecosistema)

        if self.ciclos_transcurridos_tornado % self.ciclos_tornado == 0 and random.random() < 0.6:
            self.activar_tornado()

        if self.tornado_activado:
            self.impacto_tornado(ecosistema)
            
        if self.ciclos_transcurridos_lluvia % self.ciclos_lluvia == 0 and random.random() < 0.4:
            self.activar_lluvia()

        if self.lluvia_activada:
            self.efecto_lluvia()

        # Agregar charco si llueve
        if random.random() < 0.2:
            while True:
                x_charco = random.randint(0, ANCHO)
                y_charco = random.randint(ALTO // 2, ALTO)  # Asegurarse de que estén en la parte inferior del mapa

                # Verificar si la posición del charco está fuera del suelo desértico
                if not ambiente.suelo_desertico.colliderect(pygame.Rect(x_charco, y_charco, 1, 1)):
                    charco = (x_charco, y_charco)
                    ambiente.charcos.add(charco)
                    mensaje=f"¡Ha comenzado a llover! Se formó un charco en ({x_charco}, {y_charco})."
                    print(mensaje)
                    logging.info(mensaje)
                    break

        # Actualizar el nivel de agua en función de factores abióticos
        self.agua += random.randint(-3, 3)

        # Verificar la disponibilidad de agua para los animales
        for organismo in ecosistema.organismos:
            if isinstance(organismo, Animal):
                distancia_agua = min(
                    [abs(organismo.x - x) + abs(organismo.y - y) for x, y in self.charcos],
                    default=float('inf')
                )

                if distancia_agua <= 30:  # Ajusta el valor según la distancia que consideres apropiada
                    organismo.vida += 2  # Los animales ganan vida al estar cerca del agua
                else:
                    organismo.vida -= 1  # Los animales pierden vida si están lejos del agua

                # Verificar si el animal muere por deshidratación
                if organismo.vida <= 0:
                    ecosistema.organismos.remove(organismo)
            
        # Agregar la temperatura del suelo desértico y efectos de deshidratación
        # Verificar si el organismo está en la región desértica
        for organismo in ecosistema.organismos:
            if ambiente.suelo_desertico.colliderect(pygame.Rect(organismo.x, organismo.y, 1, 1)):
                organismo.hidratacion -= 4  # Ajusta la velocidad de deshidratación en el desierto según tus necesidades

    def dibujar_suelo(self, ventana):
        pygame.draw.rect(ventana, self.color_desertico, self.suelo_desertico)

    def impacto_meteorito(self, ecosistema):
        mensaje="¡Impacto de meteorito! Todos los organismos murieron."
        print(mensaje)
        logging.info(mensaje)
        ecosistema.organismos = []
        self.ciclos_transcurridos_meteorito = 0

    def activar_tornado(self):
        mensaje="¡Tornado activado!"
        print(mensaje)
        logging.info(mensaje)
        self.tornado_activado = True
        self.tornado_efecto_activado = True
        self.tiempo_restante_tornado = 30  # Establecer la duración del efecto del tornado en ciclos

    def impacto_tornado(self, ecosistema):
        if self.tornado_efecto_activado:
            mensaje="¡Impacto de tornado!"
            print(mensaje)
            logging.info(mensaje)
            # Marcar la zona de impacto en la variable
            for organismo in ecosistema.organismos:
                if isinstance(organismo, Animal) or isinstance(organismo, Planta):
                    distancia_x = abs(self.posicion_tornado[0] - organismo.x)
                    distancia_y = abs(self.posicion_tornado[1] - organismo.y)
                    if distancia_x <= 200 and distancia_y <= 200:
                        organismo.vida = 0
                        organismo.morir("Impacto de tornado")
                        # Marcar la posición en la zona de impacto
                        self.zona_impacto_tornado.add((organismo.x, organismo.y))
                        mensaje=f"Un organismo en ({organismo.x}, {organismo.y}) murió por el tornado."
                        print(mensaje)
                        logging.info(mensaje)

    def dibujar_tornado(self, ventana):
        if self.tornado_activado:
            # Dibuja líneas que simulan la forma de un tornado
            for _ in range(10):
                x1 = int(self.posicion_tornado[0])
                y1 = int(self.posicion_tornado[1])
                x2 = random.randint(x1 - 50, x1 + 50)
                y2 = random.randint(y1 - 50, y1 + 50)
                pygame.draw.line(ventana, (0, 100, 255), (x1, y1), (x2, y2), 3)

    def avanzar_ciclo(self, ecosistema):
        self.ciclos_transcurridos_meteorito += 1
        self.ciclos_transcurridos_tornado += 1
        self.aplicar_clima(ecosistema)
        self.dibujar_suelo(ventana)  # Dibujar el suelo desértico
        self.dibujar_tornado(ventana)
        if self.ciclos_transcurridos_meteorito >= self.ciclos_meteorito:
            self.ciclos_transcurridos_meteorito = 0
        if self.ciclos_transcurridos_tornado >= self.ciclos_tornado:
            self.ciclos_transcurridos_tornado = 0
            self.tornado_activado = False  # Desactivar el tornado después de ciertos ciclos
            self.tiempo_restante_tornado = 0  # Restablecer el tiempo restante del tornado
            self.tornado_efecto_activado = False  # Desactivar el efecto del tornado
        if self.ciclos_transcurridos_lluvia % self.ciclos_lluvia == 0 and random.random() < 0.2:
            self.activar_lluvia()
        self.efecto_lluvia()
        

    def activar_lluvia(self):
        mensaje="Lluvia activada!"
        print(mensaje)
        logging.info(mensaje)
        self.lluvia_activada = True

    def efecto_lluvia(self):
        if self.lluvia_activada:
            mensaje="Efecto de lluvia..."
            print(mensaje)
            logging.info(mensaje)
            for _ in range(3):
                x_charco = random.randint(0, ANCHO // 2)
                y_charco = random.randint(0, ALTO // 2)
                self.charcos.add((x_charco, y_charco))  

            self.lluvia_activada = False
    def pintar_charco(self):
        # Dibujar charcos en la pantalla
        for charco in ambiente.charcos:
            pygame.draw.circle(ventana, (0, 100, 255), charco, 5)  # Ajusta el radio según tus preferencias



class Ecosistema:
    def __init__(self):
        self.organismos = []
        self.contador_animales = {}

    def actualizar_contador_animales(self):
        self.contador_animales = {}  # Reinicia el diccionario
        for organismo in self.organismos:
            if isinstance(organismo, Animal):
                especie = organismo.especie
                self.contador_animales[especie] = self.contador_animales.get(especie, 0) + 1
    def configurar_cantidad_animales(self):
        cantidad_cebras = int(input("Ingrese la cantidad de cebras: "))
        cantidad_leones = int(input("Ingrese la cantidad de leones: "))
        cantidad_tigres = int(input("Ingrese la cantidad de tigres: "))
        cantidad_antilopes = int(input("Ingrese la cantidad de antílopes: "))
        cantidad_yenas = int(input("Ingrese la cantidad de hienas: "))
        cantidad_jirafas = int(input("Ingrese la cantidad de jirafas: "))
        cantidad_lobos = int(input("Ingrese la cantidad de lobos: "))
        cantidad_bufalos = int(input("Ingrese la cantidad de búfalos: "))

        for _ in range(cantidad_leones):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal(random.randint(0, ANCHO),random.randint(0, ALTO),100, 100,10,"León","Carnívora",random.choice(["macho", "hembra"]),))

        for _ in range(cantidad_cebras):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal( random.randint(0, ANCHO),random.randint(0, ALTO),100,100,8, "Cebra","Herbívora",random.choice(["macho", "hembra"]),))
        for _ in range(cantidad_tigres):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal(random.randint(0, ANCHO),random.randint(0, ALTO),100, 100,10,"Tigre","Carnívora",random.choice(["macho", "hembra"]),))

        for _ in range(cantidad_antilopes):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal( random.randint(0, ANCHO),random.randint(0, ALTO),100,100,8, "Antilope","Herbívora",random.choice(["macho", "hembra"]),))
        for _ in range(cantidad_yenas):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal(random.randint(0, ANCHO),random.randint(0, ALTO),100, 100,10,"Yena","Carnívora",random.choice(["macho", "hembra"]),))

        for _ in range(cantidad_jirafas):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal( random.randint(0, ANCHO),random.randint(0, ALTO),100,100,8, "Jirafa","Herbívora",random.choice(["macho", "hembra"]),))
        for _ in range(cantidad_lobos):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal(random.randint(0, ANCHO),random.randint(0, ALTO),100, 100,10,"Lobos","Carnívora",random.choice(["macho", "hembra"]),))

        for _ in range(cantidad_bufalos):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Animal( random.randint(0, ANCHO),random.randint(0, ALTO),100,100,8, "Bufalo","Herbívora",random.choice(["macho", "hembra"]),))

        for _ in range(50):
            # Asegúrate de pasar el argumento 'genero'
            self.organismos.append(
                Planta(random.randint(0, ANCHO), random.randint(0, ALTO), 50, 30))
    def mostrar_menu():
        print("\n--- Menú ---")
        print("1. Configurar cantidad de animales")
        print("2. Iniciar simulación")
        print("3. Salir")

    def update(self):
    # Listas para almacenar nuevos organismos y reproducciones
        nuevos_organismos = []
        reproducciones = []

        # Iterar sobre todos los organismos existentes
        for organismo in self.organismos:
            # Mover el organismo actual
            organismo.mover()

            # Iterar nuevamente para interacciones entre organismos
            for otro_organismo in self.organismos:
                if organismo != otro_organismo:
                    # Interacción: Animal Herbívoro cazando Planta
                    if (
                        isinstance(otro_organismo, Planta)
                        and isinstance(organismo, Animal)
                        and organismo.dieta == "Herbívora"
                    ):
                        organismo.alimentarse(otro_organismo, self.organismos)
                    # Interacción: Animal Carnívoro cazando Animal Herbívoro
                    elif (
                        isinstance(otro_organismo, Animal)
                        and isinstance(organismo, Animal)
                        and organismo.dieta == "Carnívora"
                        and otro_organismo.dieta == "Herbívora"
                    ):
                        organismo.cazar(otro_organismo)
                        if otro_organismo.vida <= 0:
                            # Eliminar presa si muere por la caza
                            self.organismos.remove(otro_organismo)
                            mensaje=f"El {otro_organismo.especie} ha muerto por caza. Energía del cazador: {organismo.energia}"
                            print(mensaje)
                            logging.info(mensaje)
            if organismo.vida <= 0:
                if isinstance(organismo, Animal):
                   self.organismos.remove(organismo)
                   mensaje = f"Un {organismo.especie} ha muerto por {organismo.razon_muerte}."
                   print(mensaje)
                   logging.info(mensaje)

                # Crear un cadáver para el animal
                   cadaver = Cadaver(organismo.x, organismo.y, organismo.especie)
                   self.organismos.append(cadaver)
                else:
                # Si no es un animal, simplemente eliminar el organismo
                   self.organismos.remove(organismo)
                   mensaje = f"Un {organismo.especie} ha muerto por {organismo.razon_muerte}."
                   print(mensaje)
                   logging.info(mensaje)

        # Agregar nuevos organismos generados durante reproducción
        for reproduccion in reproducciones:
            self.organismos.append(reproduccion)

        # Realizar acciones específicas para las plantas y generar nuevas plantas
        for organismo in self.organismos:
            if isinstance(organismo, Planta):
                organismo.fotosintesis()
                nueva_planta = organismo.reproducir()
                if nueva_planta:
                    nuevos_organismos.append(nueva_planta)

        # Agregar nuevas plantas a la lista principal de organismos
        self.organismos.extend(nuevos_organismos)
        self.actualizar_contador_animales()

# Función para mostrar el menú



# Ciclo principal del simulador
reloj = pygame.time.Clock()
ecosistema = Ecosistema()
ambiente = Ambiente()

while True:
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ecosistema.configurar_cantidad_animales()
        elif opcion == "2":
            while True:
                # Manejar eventos de pygame, como cerrar la ventana
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                # Avanzar el ciclo en el ambiente y actualizar el ecosistema
                ambiente.avanzar_ciclo(ecosistema)
                ecosistema.update()

                # Limpiar la ventana con un fondo blanco y dibujar el suelo del ambiente
                ventana.fill((255, 255, 255))
                ambiente.dibujar_suelo(ventana)
                
                # Iterar sobre los organismos en el ecosistema y aplicar lógica específica
                for organismo in ecosistema.organismos.copy():
                    if isinstance(organismo, Animal):
                        # Realizar acciones específicas para animales, como beber agua y moverse
                        organismo.beber_agua(ambiente)
                        organismo.mover()
                        organismo.vida -= 0.5
                        # Verificar si el animal ha muerto y realizar acciones adicionales
                        if organismo.vida <= 0:
                            mensaje=f"Un {organismo.especie} ha muerto por {organismo.razon_muerte}."
                            print(mensaje)
                            logging.info(mensaje)
                            # Remover el animal muerto de los charcos si estaba en alguno
                            for charco in ambiente.charcos.copy():
                                if (organismo.x, organismo.y) in charco:
                                    ambiente.charcos.remove(charco)
                    elif isinstance(organismo, Planta):
                        # Realizar acciones específicas para plantas, como fotosíntesis y reproducción
                        organismo.fotosintesis()
                        nueva_planta = organismo.reproducir()
                        # Agregar la nueva planta al ecosistema si se reproduce
                        if nueva_planta:
                            ecosistema.organismos.append(nueva_planta)
                

                # Agrega la reproducción de animales dentro del bucle principal
                cebras = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Cebra"]
                leones = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "León"]
                tigres = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Tigre"]
                antilope = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Antilope"]
                yena = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Yena"]
                jirafa = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Jirafa"]
                lobos = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Lobos"]
                bufalo = [org for org in ecosistema.organismos if isinstance(org, Animal) and org.especie == "Bufalo"]

                for organismo in ecosistema.organismos.copy():
                    if isinstance(organismo, Animal):
                        # Verificar si hay cebras y leones antes de intentar reproducción
                        if organismo.especie == "León" and leones:
                            pareja_reproduccion = random.choice(leones)
                        elif organismo.especie == "Tigre" and tigres:
                            pareja_reproduccion = random.choice(tigres)
                        elif organismo.especie == "Antilope" and antilope:
                            pareja_reproduccion = random.choice(antilope)
                        elif organismo.especie == "Yena" and yena:
                            pareja_reproduccion = random.choice(yena)
                        elif organismo.especie == "Jirafa" and jirafa:
                            pareja_reproduccion = random.choice(jirafa)
                        elif organismo.especie == "Lobos" and lobos:
                            pareja_reproduccion = random.choice(lobos)
                        elif organismo.especie == "Bufalo" and bufalo:
                            pareja_reproduccion = random.choice(bufalo)
                        else:
                            continue  # No hay pareja de reproducción disponible

                        nuevo_animal = organismo.reproducirse(pareja_reproduccion)
                        if nuevo_animal:
                            ecosistema.organismos.append(nuevo_animal)
                            mensaje=f"¡Un {organismo.especie} macho y una hembra se reprodujeron y crearon un nuevo {nuevo_animal.especie} en ({nuevo_animal.x}, {nuevo_animal.y})!"
                            print(mensaje)
                            logging.info(mensaje)
                for organismo_1 in ecosistema.organismos:
                    for organismo_2 in ecosistema.organismos:
                        if isinstance(organismo_1, Animal) and isinstance(organismo_2, Animal):
                            organismo_1.pelear(organismo_2)
                # Iterar sobre los organismos en el ecosistema y dibujarlos en la ventana
                for organismo in ecosistema.organismos:
                    if isinstance(organismo, Animal):
                        if organismo.especie == "Cebra":
                            color = (128, 255, 255)
                        elif organismo.especie == "León":
                            color = (255, 128, 255)
                        elif organismo.especie == "Tigre":
                            color = (255, 128, 0)
                        elif organismo.especie == "Antilope":
                            color = (255, 0, 255)
                        elif organismo.especie == "Yena":
                            color = (128, 0, 0)
                        elif organismo.especie == "Jirafa":
                            color = (255, 255, 0)
                        elif organismo.especie == "Lobos":
                            color = (128, 128, 128)
                        elif organismo.especie == "Bufalo":
                            color = (128, 255, 0)
                        elif organismo.cadaver:
            # Dibujar el cadáver en rojo
                         pygame.draw.rect(ventana, (255, 0, 0), pygame.Rect(organismo.cadaver.x - 5, organismo.cadaver.y - 5, 10, 10))

                        else:
                            color = (0, 0, 255)
                    elif isinstance(organismo, Planta):
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)

                    pygame.draw.rect(ventana, color, pygame.Rect(organismo.x - 5, organismo.y - 5, 10, 10))
                
                # Dibujar el lago en el centro del ecosistema
                pygame.draw.circle(ventana, (0, 100, 255), ambiente.posicion_lago, 100)
                # Agrega la visualización del tornado
                ambiente.dibujar_tornado(ventana)
                # Dibujar charcos en la pantalla
                ambiente.pintar_charco()
                logging.info("Fin de la simulación")

                ambiente.dibujar_contador_animales(ventana, ecosistema)
                pygame.display.flip()
                reloj.tick(1)
        elif opcion == "3":
            pygame.quit()
            sys.exit()
        else:
            print("Opción no válida. Por favor, ingrese una opción válida.")
