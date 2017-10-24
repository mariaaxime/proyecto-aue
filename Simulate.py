# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 11:32:22 2016

@author: Alejandro Betancourt Espinel
"""

import Estructuras as estruct
import matplotlib.pyplot as pyl

"""
Programa que ejecuta una simulación basado en los datos ingresados en la hoja de Excel
"""
def simular(numUsuarios, numDias, periodos):
    simu = []
    total =[]
    #Se crea una nueva población
    pop  = estruct.Population(numUsuarios, periodos)
    #inicializan los usuarios
    pop.initUsers(periodos)
    #Lista que guarda el encabezado de la salida de excel
    #Guarda las etiquetas: día, periodo, nombres de cada aparato y el total
    #Se ejecuta la simulación según el número de días definidos
    #Se almacena la información de cada día simulado
    # Se agrega la información a la lista Total
    for k in range(numDias):
        pop.goDay(periodos)
        for j in range(periodos):
            s = {}
            #Se listan los días y los periodos para imprimir
            dia = k+1
            periodo = j+1
            suma = 0
            #suma las cargas de los usuarios por cada día , según aparatos y la carga total
            for i in range(len(estruct.aparatos)):
                aparato = estruct.aparatos[i]["Nombre"]
                consumo = pop.appliancesCharge[i][j]
                suma += pop.appliancesCharge[i][j]
                s["dia"] = dia
                s["periodo"] = periodo
                s[aparato] = consumo
                #s["consumo"] = consumo
            total = suma
            s["total"] = total
            simu.append(s)

    return simu

"""
Función de prueba para graficar el consumo dela población
"""
def enviar():
    pop  = estruct.Population(2)
    pop.initUsers()
    listaAcum=[0.0]*estruct.prueba
    total =[]
    dias = list(range(1))
     
    for k in range(1):
        consumoDia = 0
        consumoDia =  0
        pop.goDay()
        for i in range(len(pop.users)):
            print(pop.users[i].name)
            print(pop.users[i].profile)
            print(len(pop.users[i].appliances))
            for j in range(len(pop.users[i].appliances)):
               print(pop.users[i].appliances[j].name)
               print(pop.users[i].appliances[j].power)
               print(pop.users[i].appliances[j].rndOn)
               print(pop.users[i].appliances[j].onHour)
               print(pop.users[i].appliances[j].rndSpan)
               print(pop.users[i].appliances[j].span)
               print(pop.users[i].appliances[j].offHour)
               print(pop.users[i].appliances[j].use)
               pyl.plot(pop.users[i].appliances[j].chargeUse,color='b')
               pyl.grid(True)
               pyl.title(pop.users[i].appliances[j].name)
               pyl.show()
               print(pop.users[i].appliances[j].chargeUse)
            pyl.plot(pop.users[i].charge,color = 'r')
            pyl.grid(True)
            pyl.title('Consumo ' + pop.users[i].name)
            pyl.show()
            print(pop.users[i].charge)
        #pyl.plot(pop.dailyCharge,color ='g')
        #pyl.grid(True)
        #pyl.title('Consumo Población por día')
        #pyl.show()
       # print(pop.dailyCharge)
        listaAcum = [x+y for (x,y) in zip(pop.dailyCharge,listaAcum) ]
        pyl.plot(listaAcum,color ='c')
        pyl.grid(True)
        pyl.title('Consumo Población Acumulado')
        pyl.show()
        print(listaAcum)    
        consumoDia = sum(pop.dailyCharge)
        print(consumoDia)
        total.append(consumoDia)
    pyl.bar(dias,total,1,color = 'm')
    pyl.grid(True)
    pyl.title('Consumo total por día')
    pyl.show()
    print(dias)
    print(total)
    print('Total Mes')
    print(sum(total))
