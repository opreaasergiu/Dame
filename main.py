# Jocul de Dame
from copy import deepcopy
from collections import namedtuple
from math import inf
from enum import IntEnum
import time

Mutare = namedtuple('Mutare', ('jucator', 'pozitie_initiala', 'pozitie_finala'))

class afisare:
    # Afisare tabla curenta
    def afis_configuratie(self, configuratie):
        afisare_tabla(configuratie.tabla)

    # Verifica daca mutarea este posibila si, daca este, o executa
    def mutare(self, configuratie, jucator, mutari_posibile):
        start_timp = time.time()
        while True:
            print("Introdu coordonate piesa si coordonate mutare.\nexit - Inchide")

            linie = input()
            if linie == 'exit':
                return None

            try:
                x1, y1, x2, y2 = map(int, linie.split())
            except ValueError:
                print("Coordonate invalide! Incearca din nou!\n")
                continue

            pozitie_actuala = (x1, y1)
            pozitie_noua = (x2, y2)

            mutare = Mutare(jucator, pozitie_actuala, pozitie_noua)

            if mutare not in mutari_posibile:
                print("Mutare invalida! Incearca din nou!\n")
                continue

            sfarsit_timp = time.time()
            print(f"Jucatorul s-a gandit: {sfarsit_timp - start_timp} secunde.")

            return mutare


# Afisare tabla
def afisare_tabla(tabla):
    print(" ", ' '.join(str(i) for i in range(8)))
    for i, linie in enumerate(tabla):
        print(i, ' '.join(str(piesa) for piesa in linie))

class Jucator(IntEnum):
    negru = 1
    alb = 2

    # Returneaza culoarea opusa
    def inverseaza_culoarea(self):
        if self == self.negru:
            return self.alb
        return self.negru

    def testeaza_negru(self):
        return self == self.negru


class Piesa(IntEnum):
    nimic = 0
    negru = 1
    alb = 2
    rege_negru = 3
    rege_alb = 4

    # Afisare piese
    def __str__(self):
        if self == self.negru:
            return '●'
        if self == self.alb:
            return '○'
        if self == self.rege_negru:
            return 'N'
        if self == self.rege_alb:
            return 'A'
        return ' '

    # Intoarce jucatorul care detine piesa
    def jucator_detine(self):
        if self == self.negru or self == self.rege_negru:
            return Jucator.negru
        return Jucator.alb

    # Testeaza daca piesa e rege
    def testeaza_rege(self):
        if self == self.rege_negru or self == self.rege_alb:
            return True
        return False


class Joc:
    def __init__(self, tabla):
        self.tabla = tabla
        self.lant = False  # True daca jucatorul poate sa captureze mai multe piese in lant
        self.piesa_lant = None

    # Creare tabla initiala
    def tabla_initiala():
        # Creare tabla goala
        tabla = []
        for i in range(8):
            linie = []
            for j in range(8):
                linie.append(Piesa.nimic)
            tabla.append(linie)

        # Adaugare piese
        for linie in range(3):
            for coloana in range((linie + 1) % 2, 8, 2):
                tabla[linie][coloana] = Piesa.alb

            for coloana in range(linie % 2, 8, 2):
                tabla[7 - linie][coloana] = Piesa.negru

        return Joc(tabla)

    # Intoarce o lista ce contine toate pozitiile pieselor unui jucator
    def lista_pozitii_piese(self, jucator):
        lista = []
        for linie, sir in enumerate(self.tabla):
            for coloana, piesa in enumerate(sir):
                if piesa != Piesa.nimic and piesa.jucator_detine() == jucator:
                    lista.append([linie, coloana])
        return lista

    # Numarul de piese ale unui jucator
    def nr_piese(self, jucator):
        suma = 0
        for i in self.lista_pozitii_piese(jucator):
            suma += 1

        return suma

    # O lista cu toate mutarile posibile ale unei piese ale unui jucator
    def mutari_posibile_piesa(self, jucator, linie, coloana):

        piesa = self.tabla[linie][coloana]
        pozitie_curenta = (linie, coloana)
        oponent = jucator.inverseaza_culoarea()

        # Definim cum se pot misca regele
        if piesa.testeaza_rege():
            mutari_permise = (-1, 1)
        else:
            if jucator == Jucator.alb:
                mutari_permise = (1,)
            else:
                mutari_permise = (-1,)

        miscari_simple = []
        miscari_puncte = []

        for mutare in mutari_permise:
            linie_noua = linie + mutare
            if not (0 <= linie_noua <= 7):
                continue
            for coloane_posibile in (-1, 1):
                coloana_noua = coloana + coloane_posibile

                # Daca avem loc pe tabla
                if not (0 <= coloana_noua <= 7):
                    continue
                pozitie_noua = (linie_noua, coloana_noua)
                piesa_poz_noua = self.tabla[linie_noua][coloana_noua]

                # Daca avem celula goala
                if piesa_poz_noua == Piesa.nimic:
                    miscari_simple.append(Mutare(jucator, pozitie_curenta, pozitie_noua))

                # Daca capturam pisele oponentului, trebuie sa verificam daca putem sari peste ele 
                # si sa gasim o celula goala
                elif piesa_poz_noua.jucator_detine() == oponent:
                    linie_oponent = linie_noua + mutare
                    coloana_oponent = coloana_noua + coloane_posibile
                    pozitie_dupa_captura = (linie_oponent, coloana_oponent)

                    # Sa nu depasim limitele tablei si celula sa fie goala
                    if (0 <= linie_oponent <= 7 and 0 <= coloana_oponent <= 7):
                        aux = self.tabla[linie_oponent][coloana_oponent]
                        if aux == Piesa.nimic:
                            miscari_puncte.append(Mutare(jucator, pozitie_curenta, pozitie_dupa_captura))

        return miscari_simple, miscari_puncte

    # Modificarea tablei dupa mutare
    def modificare_tabla(self, mutare):
        jucator, (x1, y1), (x2, y2) = mutare

        copie_tabla = deepcopy(self.tabla)

        copie_tabla[x2][y2] = self.tabla[x1][y1]
        copie_tabla[x1][y1] = Piesa.nimic

        if jucator == Jucator.negru and x2 == 0:
            copie_tabla[x2][y2] = Piesa.rege_negru
        if jucator == Jucator.alb and x2 == 7:
            copie_tabla[x2][y2] = Piesa.rege_alb

        if abs(y2 - y1) > 1:
            mutare = True
        else:
            mutare = False

        # Daca avem mutare cu saritura peste oponent, stergem piesa oponentului
        if mutare:
            linie = (x1 + x2) // 2
            coloana = (y1 + y2) // 2
            copie_tabla[linie][coloana] = Piesa.nimic

        configuratie_noua = Joc(copie_tabla)

        if mutare:
            miscari_simple, miscari_puncte = configuratie_noua.mutari_posibile_piesa(jucator, x2, y2)
            if miscari_puncte:
                configuratie_noua.lant = True
                configuratie_noua.piesa_lant = (x2, y2)

        return configuratie_noua

    # Returneaza o lista cu mutarile posibile ale unui jucator
    def mutari_posibile_jucator(self, jucator):
        # Testam daca avem posibilitatea de a captura mai multe piese intr-o singura mutare
        if self.lant == True:
            linie, coloana = self.piesa_lant
            miscari_simple, miscari_puncte = self.mutari_posibile_piesa(jucator, linie, coloana)
            return miscari_puncte

        mutari = []

        for linie, coloana in self.lista_pozitii_piese(jucator):
            miscari_simple, miscari_puncte = self.mutari_posibile_piesa(jucator, linie, coloana)
            mutari += miscari_simple
            mutari += miscari_puncte

        return mutari

    def configuratii_posibile(self, jucator):
        mutari_posibile = self.mutari_posibile_jucator(jucator)

        configuratii = []
        for mutare in mutari_posibile:
            configuratii.append(self.modificare_tabla(mutare))

        return configuratii

    def scor(self):
        regi_negri = 0
        regi_albi = 0
        piese_negre = 0
        piese_albe = 0

        for linie, coloana in self.lista_pozitii_piese(Jucator.negru):
            piesa_aux_scor = self.tabla[linie][coloana]
            if piesa_aux_scor.testeaza_rege():
                regi_negri += 1
            else:
                piese_negre += 1

        for linie, coloana in self.lista_pozitii_piese(Jucator.alb):
            piesa_aux_scor = self.tabla[linie][coloana]
            if piesa_aux_scor.testeaza_rege():
                regi_albi += 1
            else:
                piese_albe += 1

        return (3 * regi_negri + piese_negre) - (3 * regi_albi + piese_albe)

    def scor1(self):
        return self.nr_piese(Jucator.negru) - self.nr_piese(Jucator.alb)


# Gaseste cea mai buna mutare pentru calculator
def cea_mai_buna_mutare(config, jucator, adancime_max, retezare):
    # Generarea tuturor configuratiilor posibile
    configuratii_posibile = config.configuratii_posibile(jucator)

    if retezare == True:
        algoritm = alpha_beta
    else:
        algoritm = minimax

    oponent = jucator.inverseaza_culoarea()
    scoruri = {}

    # Pentru fiecare mutare posibila, stabilim un scor
    for configuratie in configuratii_posibile:
        # Daca avem mutari consecutive posibile, le facem pe toate
        if configuratie.lant:
            mutare_urmatoare = jucator
        else:
            # Altfel, pasam mutarea omului
            mutare_urmatoare = oponent

        # Aici se decide scorul unei configuratii
        scor = algoritm(configuratie, mutare_urmatoare, adancime_max)

        # Adaugare la dictionarul de scoruri
        scoruri[configuratie] = scor

    if jucator.testeaza_negru():
        optimum_func = max
    else:
        optimum_func = min

    # Returneaza scorul maxim dintre toate scorurile configuratiilor obtinute
    return optimum_func(configuratii_posibile, key=lambda x: scoruri[x])


# Algoritmul Minimax
def minimax(configuratie, jucator, adancime):
    if adancime == 0:
        return configuratie.scor()

    # Generarea tuturor configuratiilor posibile
    configuratii_posibile = configuratie.configuratii_posibile(jucator)

    oponent = jucator.inverseaza_culoarea()

    # Scor initial
    if jucator.testeaza_negru():
        scor = -inf
    else:
        scor = +inf

    # Calculam scorurile
    for configuratie in configuratii_posibile:
        # Daca avem lant, luam toate mutarile posibile
        if configuratie.lant:
            mutare_urmatoare = jucator
        else:
            mutare_urmatoare = oponent

        urmatorul_scor = minimax(configuratie, mutare_urmatoare, adancime - 1)

        if jucator.testeaza_negru():
            scor = max(scor, urmatorul_scor)
        else:
            scor = min(scor, urmatorul_scor)

    return scor


# Algoritmul Alpha-Beta
def alpha_beta(configuratie, jucator, adancime, alpha=-inf, beta=+inf):
    # Testam daca am epuizat adancimea arborelui
    if adancime == 0:
        return configuratie.scor()

    # Generarea tuturor configuratiilor posibile
    configuratii_posibile = configuratie.configuratii_posibile(jucator)

    oponent = jucator.inverseaza_culoarea()

    # Scor initial
    if jucator.testeaza_negru():
        scor = -inf
    else:
        scor = +inf

    for configuratie in configuratii_posibile:
        # Daca avem lant, luam toate mutarile posibile
        if configuratie.lant:
            mutare_urmator = jucator
        else:
            mutare_urmator = oponent

        urmatorul_scor = alpha_beta(configuratie, mutare_urmator, adancime - 1, alpha, beta)

        if jucator.testeaza_negru():
            scor = max(scor, urmatorul_scor)
            alpha = max(alpha, scor)
        else:
            scor = min(scor, urmatorul_scor)
            beta = min(beta, scor)

        if alpha >= beta:
            break

    return scor


if __name__ == '__main__':
    # Alegere dificultate
    adancime_max = None
    while adancime_max is None:
        print("Alege nivelul de dificultate:\n1. Usor\n2. Mediu\n3. Greu\n ")
        alegere = int(input())

        if alegere == 1:
            adancime_max = 1
        else:
            if alegere == 2:
                adancime_max = 3
            else:
                if alegere == 3:
                    adancime_max = 5
                else:
                    print("Alegere invalida!\n")

    # Alegere algoritm
    retezare = None
    while retezare is None:
        print("\nAlege Algoritmul:\n1. Minimax\n2. Alpha-Beta Pruning\n")

        alegere = int(input())

        if alegere == 1:
            retezare = False
        else:
            if alegere == 2:
                retezare = True
            else:
                print("Alegere invalida!\n")

    # Alegere culoare piese
    om = None
    while om is None:
        print("\nAlege culoarea:\n1. Negru\n2. Alb\n")

        alegere = int(input())

        if alegere == 1:
            om = Jucator.negru
        else:
            if alegere == 2:
                om = Jucator.alb
            else:
                print("Alegere invalida!\n")

    computer = om.inverseaza_culoarea()
    print("\nAi ales: ", om, "\nComputerul joaca cu: ", computer)
    interfata = afisare()

    castigator = None
    configuratie_curenta = Joc.tabla_initiala()
    jucator_curent = Jucator.negru

    nr_mutari = 0
    start_timp = time.time()

    while True:
        nr_mutari += 1

        print("\nScor Negru:", configuratie_curenta.scor())
        print("Scor Alb:", (-1) * configuratie_curenta.scor())
        interfata.afis_configuratie(configuratie_curenta)

        if configuratie_curenta.nr_piese(computer) == 0:
            castigator = om
            break

        if configuratie_curenta.nr_piese(om) == 0:
            castigator = computer
            break

        mutari_posibile = configuratie_curenta.mutari_posibile_jucator(jucator_curent)

        # Verificare stare finala (partea a 2a)
        if not mutari_posibile:
            # Remiza
            break

        # Mutare om
        if jucator_curent == om:
            mutare = interfata.mutare(configuratie_curenta, jucator_curent, mutari_posibile)

            if mutare is None:
                break

            configuratie_curenta = configuratie_curenta.modificare_tabla(mutare)
        # Mutare computer
        else:
            start_timp = time.time()
            configuratie_curenta = cea_mai_buna_mutare(configuratie_curenta, computer, adancime_max, retezare)
            sfarsit_timp = time.time()

            print(f"Calculatorul s-a gandit {sfarsit_timp - start_timp} secunde.")

        # Verificam daca jucatorul curent poate sa faca mai multe mutari consecutive, va fi randul lui si mutarea urmatoare
        # Altfel, e randul celuilalt jucator
        if not configuratie_curenta.lant:
            jucator_curent = jucator_curent.inverseaza_culoarea()

    if castigator is None:
        print("\nRemiza\n")
    else:
        print("\nCastigator: ", castigator)

    print("\nScor Negru: ", configuratie_curenta.scor())
    print("Scor Alb: ", (-1) * configuratie_curenta.scor())

    print(f"\nJocul s-a terminat dupa {nr_mutari} mutari.")
    print(f"Jocul s-a terminat dupa {time.time() - start_timp} secunde.")