# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 16:18:06 2016

@author Alejandro Betancourt Espinel
r"""
#import Probas as pe
import Entrada as en
import numpy as np
"""
Archivo que contienen las clases para ejecutar el programa
"""
aparatos = en.aparatos
#Lista de perfiles tomada del programa Entrada
misPerfiles = []
misPerfiles = en.perfi

#Función que retorna un diccionario por nombre, busca en la lista de diccionarios de aparatos y
#retorna el diccionario del aparato con el nombre enviado por parámetro
#Argumentos: Nombre: nombre del aparato que se desea buscar en la lista
#Retorno: diccionario con la información del aparato.
def getDictbyName(nombre):
    dicttemp={}
    indice = next(index for (index,d) in enumerate(aparatos) if d['Nombre'] == nombre)
    dicttemp = aparatos[indice]
    return dicttemp
"""
Clase que modela un aparato
Atributos:
dataDict: diccionario con la información de potencia, nombre , cantidad y probabilidades de hora inicio y duración de un aparato
name: Nombre del aparato
power: potencia del aparato
use: lista de binarios  que representa los peridos ingresados, se utiliza para indicar si el aparato se usa o no en un lapso de periodo
chargeUse: lista de flotantes, que representa la potencia consumida por el aparato en los periodos, se usa en paralelo con use
amount: cantidad de aparatos a usar.
remainder: En el caso de que el aparto exceda los periodos de un día guarda el sobrante para el día siguiente.
onHour: Periodo en que se encendió el aparato.
offHour: Periodo en la que se apaga el aparato.
span: Duración en periodos del aparato encendido.
rndOn: Número pseudoaleatorio relacionado con la hora de inicio del aparato
rdnSpan: Número pseudoaleatorio relacionado con la duración del aparato encedido.
Métodos:
_init_: Inicializa un nuevo aparato:
getInit_End_Reminder: Asigna valores a periodo de inicio, periodo fin y duración
updatePastInfo: Actualiza la información de días anteriores
daily_Use: actualiza las listas de uso y de carga de uso en el aparato según las horas inicio y fin
resetUse: los valores de la lista de uso se vuelven a falso y los valores de carga a cero
"""
class Aparato():

   #Inicializar, crea un aparato con nombre, potencia, cantidad e inicializa sus respectivos atributos en cero
   #Argumentos, nombre: nombre del aparato a crear(debe estar en la lista de los datos de entrada)
    def __init__(self,aparato, numperiodos):
        self.dataDict = getDictbyName(aparato['nombre'])
        self.name = self.dataDict['Nombre']
        self.power = aparato['potencia']#self.dataDict['Potencia']
        self.use = [False] *numperiodos
        self.resetUse(numperiodos)
        self.chargeUse =[0.0] * numperiodos
        self.amount = aparato['cantidad']#self.dataDict['Cantidad']
        self.remainder = 0
        self.onHour = 0
        self.offHour = 0
        self.span  = 0
        self.rndOn= 0.0
        self.rndSpan = 0.0
    #Por medio de pseudoaleatorios y con la probabilidad de periodos de inicio y duración icluidas en el dataDict, se establece
    #La hora inicio, duración y horafin del aparato.
    # También se calcula el  remanente para el día siguiente en caso de existir.
    def getInit_End_Reminder(self, numperiodos):
        #Cambia la semilla del generador de pseudoaleatorios, para evitar números iguales
        np.random.seed()
        self.rndOn = np.random.random()
        np.random.seed()
        self.rndSpan = np.random.random()
        for i in range(len(self.dataDict['Horas Inicio'])):
            if self.rndOn <= self.dataDict['Horas Inicio'][i][1]:
                self.onHour = self.dataDict['Horas Inicio'][i][0]
                break
        if self.onHour != -1:
            index1 = next(index for (index,d) in enumerate(self.dataDict['Duracion']) if d['Hora Inicio'] == self.onHour)
            for i in range(len(self.dataDict['Duracion'][index1]['Duraciones'])):
                if self.rndSpan <= self.dataDict['Duracion'][index1]['Duraciones'][i][1]:
                    self.span = self.dataDict['Duracion'][index1]['Duraciones'][i][0]
                    self.offHour = self.onHour + self.span
                    break
        else:
                self.span = -1
                self.offHour = -1
        if self.offHour > numperiodos:
            self.remainder = self.offHour - numperiodos
            self.offHour = numperiodos
    #Actualiza en las listas de uso y de carga, el remanete del día anterior y vuelve el remanente a cero.
    def updatePastInfo(self,residuo):
        for i in range(0,int(residuo)):
            self.use[i] = True
            self.chargeUse[i] = self.power*self.amount
    #Según la hora de inicio y fin simuladas, actualiza los valores en la lista de usos y de carga
    def daily_use(self):
        if self.onHour != -1:
            for i in range(int(self.onHour),int(self.offHour)):
                self.use[i]= True
                self.chargeUse[i] = self.power*self.amount
    #Vuelve al estado inicial las listas de uso y carga (falso y cero respectivamente)
    def resetUse(self, numperiodos):
        for i in range(len(self.use)):
            self.use[i]= False
        self.chargeUse =[0.0]*numperiodos
"""
Clase que modela un usuario en una población.
Atributos:
name: Nombre del usuario
profile: Número del perfil asignado a este usuario
appliances: lista de aparatos que tiene el usuario los cuales definiran su consumo
charge: lista de la carga total consumida en cada periodo ( suma de todas las cargas de sus aparatos)
Métodos:
_init_: Crea un nuevo usuario con su nombre e inicializa los otros atributos
setAppliances: Asigna un perfil al  usuario y llena la lista de aparatos que  tiene el usuario.
runDay: Para cada aparato en la lista de aparatos simula el consumo de un día, calcula el consumo total del usuario por día
clearCharge: Vuelve la lista de carga a su estado inicial, todos los espacios en cero
"""
class Usuario():
    name = ''
    profile = 0
    # Inicializa un nuevo usuario
    #Argumentos, nom: Nombre del usuario a crear
    def __init__(self, nom, numperiodos):
        self.name = nom
        self.charge = [0.0]*numperiodos
        self.clearCharge
        self.appliances = []
        self.profile = 0
    #Por medio de pseudoaleatorios y con la información de la probailidad almacenada en la lista misPerfiles, se establece el
    #perfil del usuario y se asignan los aparatos correspondientes.
    def setAppliances(self, numperiodos):
        np.random.seed()
        r = np.random.random()
        for i in range(len(misPerfiles)):
            if r <= misPerfiles[i]['Probabilidad']:
                self.profile = misPerfiles[i]['Perfil']
                for j in range(len(misPerfiles[i]['Aparatos'])):
                    aparatoTemp = Aparato(misPerfiles[i]['Aparatos'][j], numperiodos)
                    self.appliances.append(aparatoTemp)  
                break
    #Para cada aparato asignado al usuario, se simula un día llamando los métodos de cada aparato,
    #adicionalmente se tiene en cuenta el cálculo del remanente par cada aparato.
    #Finalmente, cada vez que un aparato simula su consumo la lista de carga del usuario se actualiza, sumando la potencia en cada periodo
    def runDay(self, numperiodos):
        index = 0
        for i in range(len(self.appliances)):
            self.appliances[i].resetUse(numperiodos)
            if 'AM' in self.appliances[i].name  :
                p = self.appliances[i].name.find('AM')
                s = self.appliances[i].name[0:p]
                index = next(ind for (ind,d) in enumerate(self.appliances) if d.name == s + 'PM')
                if self.appliances[index].remainder > 0 :
                    self.appliances[i].updatePastInfo(self.appliances[index].remainder)
                    self.appliances[index].remainder = 0
                self.appliances[i].getInit_End_Reminder(numperiodos)
                self.appliances[i].daily_use()         
            elif 'PM' in self.appliances[i].name  :
                p = self.appliances[i].name.find('PM')
                s = self.appliances[i].name[0:p]
                index = next(ind for (ind,d) in enumerate(self.appliances) if d.name == s + 'AM')
                if self.appliances[index].remainder > 0 :
                    self.appliances[i].updatePastInfo(self.appliances[index].remainder)
                    self.appliances[index].remainder = 0
                self.appliances[i].getInit_End_Reminder(numperiodos)
                self.appliances[i].daily_use()         
            else:
                if self.appliances[i].remainder >0:
                    self.appliances[i].updatePastInfo(self.appliances[i].remainder)
                    self.appliances[i].remainder = 0
                self.appliances[i].getInit_End_Reminder(numperiodos)
                self.appliances[i].daily_use() 
            
            self.charge = [x+y for(x,y) in zip(self.appliances[i].chargeUse,self.charge)]
    # Convierte los valores de toda la lista de carga del usuario a cero.
    def clearCharge(self):
        for i in range(len(self.charge)):
            self.charge[i] = 0.0
"""
Clase que modela una población
Atributos:
tam: Número de usuarios que integran a la población.
users: lista que contiene a los usuarios de la población
dailyCharge: lista que almacena el consumo diario de la población por cada periodo.
appliancesCharge: lista de listas que discrimina el consumo de la población por aparatos
Métodos:
_init_: Crea una nueva población e inicializa los respectivos atributos
initUsers: Según el tamaño de la población se crean los usuarios y se llena la lista de usuarios
goDay: simula es consumo de caada usuario cada día y va acumulando el consumo en las listas de dailyCharge y appliancesCharge
"""
class Population:
    tam = 0
    users=[]
    #Inicializa una nueva población
    #Argumentos: howMuch, tamaño de la población a crear
    #La lista de usuarios se inicializa en vacio, con el número de usuarios necesarios para la población
    #Por cada aparato definido en la lista aparatos se crea una posición en appliances Charge
    def __init__(self,howMuch, numperiodos):
        self.tam = howMuch
        self.users = [None]*self.tam
        self.dailyCharge = [0.0]*numperiodos
        self.appliancesCharge=[]
        for i in range(len(aparatos)):
            listtemp=[0.0]*numperiodos
            self.appliancesCharge.append(listtemp)
    # Se crean los usuarios según el tamaño de la población con nombre Usuario 1 hasta Ususario tam
    #Se asignan los aparatos a cada usuario
    def initUsers(self, numperiodos):
        for i in range(len(self.users)):
            self.users[i] = Usuario('Usuario'+str(i+1), numperiodos)
            self.users[i].setAppliances(numperiodos)
    #Se borrann los valores de carga para días anteriores
    #Por cada usuario y cada aparato se simula un día de uso
    #se almacena la información de la carga en dailyCharge
    #Se discrimina la carga según usos.
    def goDay(self, numperiodos):
        self.dailyCharge = [0.0]*numperiodos
        for i in range(len(aparatos)):
            self.appliancesCharge[i] = [0.0]*numperiodos
        for i in range(len(self.users)):
            self.users[i].clearCharge()
            self.users[i].runDay(numperiodos)
            self.dailyCharge=[x + y for (x,y) in zip(self.users[i].charge,self.dailyCharge)]
            for j in range(len(self.users[i].appliances)):
                myInd = next(index for (index,d) in enumerate(aparatos) if d['Nombre'] == self.users[i].appliances[j].name)
                self.appliancesCharge[myInd] = [x+ y for(x,y) in zip(self.users[i].appliances[j].chargeUse,self.appliancesCharge[myInd])]
