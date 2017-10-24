# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:51:12 2016

@author: Alejandro Betancourt Espinel
"""
aparatos = []
perfi = []
"""
Función que lee los datos de las probabilidades ingresadas, en el libro de Excel y lo estructura
"""
def getprobas(probabilidades, apar, periodos):
    #Se incluye una periodo más contemplado como la probabilidad de NO USO
    horas = list(range(int(periodos) + 1))
    horas[0]= -1

    #Lee la tabla HORAS INICIO en la hoja PROBABILIDADES
    #infoInit = xl.Range('PROBABILIDADES','HORASINICIO').table.value
    #Lee las probabilidades ingresadas por aparato para hora inicio y añade un campo al diccionario creado,
    #con la llave Horas Inicio, para llenarlos en una lista de listas de la forma [hora inicio, probabilidad acumulada]
    for apa in apar:
        horas = []
        dur = []
        acum = []
        lstdur = []
        probs = 0
        for pro in probabilidades:
            for i in range(periodos+1):
                if apa == pro['aparato']:
                    horas.append(i)
                    probs += pro['inicio'][i]
                    acum.append(probs)
            final = list(zip(horas, acum))
            final = [list(x) for x in final]
        a = {}
        a["Nombre"] = apa
        #a["Cantidad"] = apa["cantidad"]
        #a["Potencia"] = apa["potencia"]
        a["Horas Inicio"] = final
        for horaIni in a["Horas Inicio"]:
            if horaIni[1] > 0:
                acm = []
                probs = 0
                for pro in probabilidades:
                    for i in range(periodos+1):
                        if apa == pro['aparato']:
                            probs += float(pro['duracion'][i])
                            acm.append(probs)
                            dur.append(i)
                last = list(zip(horas, acm))
                last = [list(x) for x in last]
                dt = {'Hora Inicio': horaIni[0], 'Duraciones': last}
                lstdur.append(dt)
        a["Duracion"] = lstdur
        aparatos.append(a)

"""
Se lee la información de los perfiles ingresados por el usuario
"""

def getProfiles(perfiles):
    global perfi
    # busca la proporción de cada perfil y crea una lista con el número de cada perfil
    # seguido de la probabilidad acumulada por cada perfil.
    perfilesProba = []
    prop = 0
    for perfil in perfiles:
        prop += float(perfil["proporcion"]) / 100
        perfilesProba.append(prop)

    numPerfiles = list(range(1,len(perfiles)+ 1))
    probsfin = [[x,y] for (x,y) in zip(numPerfiles,perfilesProba)]
    # Para cada perfil se crea un diccionario, con los campos:
    # Perfil: N° que lo identifica consecutivo
    #Aparatos: Lista de aparatos que incluye el perfil
    # Probabilidad: probabilidad acumulada calculada anteriormente para el perfil
    for perfil in perfiles:
        listatemp = []
        for aparato in perfil['aparatos']:
            listatemp.append(aparato)
        dt = {'Perfil': perfil["id"], 'Aparatos': listatemp, 'Probabilidad': probsfin[perfil["id"] - 1][1]}
        esta = -1
        for p in range(len(perfi)):
            if (perfi[p]['Perfil'] == dt['Perfil']):
                esta = p
        if (esta == -1):
            perfi.append(dt)
        else:
            perfi[esta] = dt

"""
Una vez ejecutada la función getProfiles(), la lista llamada perfiles se llena con diccionarios uno por perfil
con los campos indiccados anteriormente, a continuación se aprecia un ejemplo de la lista llena:
perfiles [ { Perfil: 1, Aparatos:[Iluminación AM, Iluminación PM, Celular], Probabilidad: 0.5},
{ Perfil: 2, Aparatos:[Iluminación AM, Iluminación PM, Celular,Televisor, Nevera], Probabilidad: 1}]
"""
#Identifica la selección del usuario para seleccionar la función que se debe llamar
# 1 = Encuesta, 2 = Manual (Probabilidades)
# if xl.Range('INICIO','SELECCION').value == 1:
#     organizeInfo()
# else:
"""
Después de ejecutar alguna de las dos funciones la lista llamada aparatos se llena con diccionarios, uno por aparato.
A continuación un ejemplo de la estructura final para la entrada de los datos.
aparatos[{Nombre: Iluminación AM, Potencia: 0.015, Cantidad: 2, Horas Inicio: [[-1,0.3],[1,0.0],[2,0.0],[3,0.0],[4,0.0],[5,0.7],[6,0.85],[7,1.0]],
 Duración: [ {Hora Inicio: -1,Duraciones: [[-1,1.0],[1,0.0],[2,0.0],[3,0.0]]}, {Hora Inicio: 5,Duraciones: [[-1,0],[1,0.4],[2,0.8],[3,0.9],[4,1.0]]}]},
 {Nombre: Iluminación PM, Potencia: 0.015, Cantidad: 2, Horas Inicio: [[-1,0.1][18,0.5],[19,0.75],[20,1.0]],
 Duración: [ {Hora Inicio: -1,Duraciones: [[-1,1.0],[1,0.0],[2,0.0],[3,0.0]]}, {Hora Inicio: 18,Duraciones: [[-1,0],[1,0.4],[2,0.8],[3,0.9],[4,1.0]]}]}]
"""
"""
IMPORTANTE!!!:
Las listas tanto de horas inicio por cada aparato, incluyen un nuúmero de sublistas igual al número de aparatos +1 (NO USO), los periodos en los que no
se enciende el aparato tienen probabilidad de cero.
Igualmente en la  lista de duraciones, sólo en las duraciones del aparatoo que sean consideradas la segunda posición tendrá un valor mayor a 0.0
"""