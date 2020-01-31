#Import genutzer Pakete
import pandas as pd
import numpy as np
import time
from itertools import product

#Herzstück des Backends. Klasse, die die Approximierung auf Basis von Werten bei Istanzierung mit der Methode 
#algorithmus ausführen durchführt. Gibt die approximierten Funktionsparameter als String, eine Tabelle mit x, sin x,
#Polynomfunc x,Fehler (x), den Fehler (Maximal bzw. Mittel) als Float, Anzahl Aufrufe der Fehlerfunktion als Integer
#und Anzahl der Iterationen als Integer zurück.
class Approximierer:
    #Initialisierung eines Approximierer Objekts
    def __init__(self, algorithmus, fehlerfunktion, algo_params_dic, polynomgrad):
        #Übergebener Algorithmus wird als Attribut (String) gespeichert
        self.auswahl_algorithmus=algorithmus
        #Übergebene Fehlerfunktion wird als Attribut (String) gespeichert
        self.auswahl_fehlerfunktion=fehlerfunktion
        #Übergebene Algorithmusparameter werden als Attribut (Dictionary) gespeichert
        self.algo_params=algo_params_dic
        #Aus dem Polynomgrad wird die Anzahl der Parameter der Polynomfunktion berechnet und als Attribut (Int) gespeichert.
        self.anzahl_params=polynomgrad+1
        #Es wird ein Array mit 1001 x-Werte von 0 bis 1000 erzeugt, die dann auf 0 bis pi/2 runterskaliert werden.
        #Wird dann als Attribut des Objekts gespeichert.
        self.x_tabellen=pd.np.array([x for x in range(1001)])
        self.x_tabellen=(self.x_tabellen/1000)*np.pi/2
        #Es wird ein Array mit den Sinus Werten für die x-Werte erzeugt. Wird dann als Attribut des Objekts gespeichert.
        self.sin_y=np.array(np.sin(self.x_tabellen))
        #Es wird ein Array erzeugt, der später zur Berechnung der Polynome genutzt wird. Diese gibt die Potenz für alle
        #Teile der Polynomfunktion an. Bsp: Polynomhgrad 3 -> Array [0,1,2,3]. Wird dann als Attribut gespeichert.
        self.power_array=np.array([x for x in range(polynomgrad+1)])
        return
    
    #Hauptmethode des Objekts. Führt abhängig vom ausgewählten Algorithmus die Approximation durch und speichert
    #die Ergebnisse.
    def algorithmus_ausführen(self):
        #Rastersuche, zunächst mit übergebenen Rasterrichtwert 100000.
        if self.auswahl_algorithmus=="Rastersuche":
            Outputs=self.Rastersuche(100000)
        #Hillclimber, zunächst mit max. Iterationen 500
        elif self.auswahl_algorithmus=="Hillclimber":
            Outputs=self.Hillclimber(500)
        #Iterierter Hillclimber, zunächst mit max. Iterationen 500
        elif self.auswahl_algorithmus=="it_Hillclimber":
            Outputs=self.it_Hillclimber(500)
        #Neu seit V1!!!!
        #Führt HAJ mit Begrenzung von 5000 Iterationen aus
        elif self.auswahl_algorithmus=="HAJ":
            Outputs=self.HAJ(5000)
        #Output speichern
        self.output_speichern(Outputs)
        return
    #Funktion zur Speicherung der Approximationsergebnisse als Attribute des Objekts. Nimmt als Input ein Dictionary mit zu
    #speichernden Elementen.
    def output_speichern(self,dic_output):
        #Funktionsparameter der Approximation als Attribut (String) speichern
        self.Params=""
        i=0
        for faktor in dic_output["Params_Liste"]:
            self.Params+=(str(faktor.round(4))+"x^"+str(i)+" ")
            i+=1
        #Fehler der Approximation als Attribut (Float) speichern
        self.fehler=dic_output["fehler"]
        #Fehler Array als Attribut speichern. Wird später aber nicht als Ausgabe genutzt.
        self.fehler_array=dic_output["fehler_array"]
        #Array mit y-Werten der Approximation als Attribut speichern. Wird später aber nicht als Ausgabe genutzt.
        self.y_array=dic_output["y_array"]
        #Anzahl der Aufrufe der Fehlerfunktion als Attribut (Int) speichern
        self.anz_aufrufe_fehlerfunktion=dic_output["anz_aufrufe_fehlerfunktion"]
        #Anzahl der Iterationen als Attribut (Int) speichern
        self.anz_iterationen=dic_output["anz_iterationen"]
        #Tabellarische Ergebnisse für Visualisierung zusammenfassen als DataFrame und als JSON String speichern.
        #Frontend kann keine DataFrames in Browsercache zwischenspeichern. Wird als Attribut gespeichert.
        self.Tabelle=pd.DataFrame({"x":self.x_tabellen, "sin_y":self.sin_y,"polynom_y":self.y_array, "fehler":self.fehler_array}).to_json(date_format='iso', orient='split')
        return
    #Neu seit V1!!!
    #Führt den Hooke and Jeeves Algorithmus aus. Nimmt Schrittweite aus Benutzereingabe entgegen. Maximale Iterationen
    #begrenzt auf zunächst 5000 (langt bis Polynomgrad 6). 
    def HAJ(self, max_it):
        #Temporäres Dictionary deklarieren. Fehler zunächst auf unendlich setzen um eine Iteration zu gewährleisten.
        dic_temp={"fehler":np.inf}
        #Startpunkt im Ursprung setzen
        dic_temp["Params_Liste"]=np.array([0 for x in range(self.anzahl_params)])
        #Anzahl Aufrufe Fehlerfunktion mit 0 initialisieren
        dic_temp["anz_aufrufe_fehlerfunktion"]=0
        #Anzahl Iterationen mit 0 initialisieren
        dic_temp["anz_iterationen"]=0
        #datatype Bugfix, array explizit als float deklarieren
        dic_temp["Params_Liste"]=dic_temp["Params_Liste"].astype(float)
        #max_it mal iterieren
        while (dic_temp["anz_iterationen"]<max_it):
            #Startpunkt zwischenspeichern
            start=dic_temp.copy()["Params_Liste"]
            #Fehler bei Startwert zwischen speichern
            start_fehler=dic_temp.copy()["fehler"]
            #i mit 0 initialisieren, wird genutzt um bei der Iteration über alle Parameter, also x^2, x^1, x^0..,zu indezieren
            i=0
            #Schritt Matrix wird mit aktueller Schrittweite berechnet
            Step=np.array([self.algo_params["Schrittweite"],0,-self.algo_params["Schrittweite"]])
            #Wird in Spaltenvektor Form gebracht
            Step=Step[np.newaxis,]
            #Explore
            #Über Anzahl Polynomgrad+1 Parameter iterieren...
            for value in dic_temp["Params_Liste"]:
                #Zeile mit aktuellen Parametern verdreifachen, einen Parameter mit Schrittweite variieren
                temp_matrix=np.repeat(dic_temp["Params_Liste"][np.newaxis,],3,axis=0)
                temp_matrix[:,i]=temp_matrix[:,i]+Step
                #Für aktuelle Parameter Variationen werden Y-Werte erzeugt.
                array_y_Werte=np.apply_along_axis(self.y_Polynome_erstellen, axis=1, arr=temp_matrix)
                #Fehlerfunktion wird mit der erzeugten Matrix. Fehler, der Index der besten Parameter im Y-Array und der Fehler
                #in Abhängigkeit von x wird zurückgegeben
                fehler_it, index_params, fehler_array_it=self.berechne_fehler(array_y_Werte)
                #Inkrementierung der Anzahl der Fehleraufrufe, um die Anzahl der Parametermöglichkeiten, die untersucht wurden.
                dic_temp["anz_aufrufe_fehlerfunktion"]+=len(temp_matrix)
                #Inkrementierung der Iterationen um 1
                dic_temp["anz_iterationen"]+=1
                #i erhöhen
                i+=1
                #Falls Verbesserung, Werte zwischenspeichern
                if fehler_it<dic_temp["fehler"]:
                    dic_temp["Params_Liste"]=temp_matrix[index_params]
                    dic_temp["fehler"]=fehler_it
                    dic_temp["fehler_array"]=fehler_array_it
                    dic_temp["y_array"]=array_y_Werte[index_params]
            #Falls nachdem alle Parameter variiert wurden, eine Verbesserung eingetreten ist, Kombinationsschritt ausführen
            if dic_temp["fehler"]<start_fehler:
                pattern_params=2*dic_temp["Params_Liste"]-start
                pattern_array=pattern_params[np.newaxis,:]
                #Für aktuelle Parameter Variationen werden Y-Werte erzeugt.
                array_y_Werte_pattern=np.apply_along_axis(self.y_Polynome_erstellen, axis=1, arr=pattern_array)
                #Fehlerfunktion wird mit der erzeugten Matrix. Fehler, der Index der besten Parameter im Y-Array und der Fehler
                #in Abhängigkeit von x wird zurückgegeben
                fehler_pattern, index_params_pattern, fehler_array_pattern=self.berechne_fehler(array_y_Werte_pattern)
                dic_temp["anz_aufrufe_fehlerfunktion"]+=1
                #Falls Kombinationsschritt besser, Werte zwischenspeichern
                if fehler_pattern<dic_temp["fehler"]:
                    dic_temp["Params_Liste"]=pattern_array[index_params_pattern]
                    dic_temp["fehler"]=fehler_pattern
                    dic_temp["fehler_array"]=fehler_array_pattern
                    dic_temp["y_array"]=array_y_Werte[index_params_pattern]
            #Falls keine Verbesserung eingetreten ist, Schrittweite halbieren
            else:
                self.algo_params["Schrittweite"]/=2
        #Dictionary mit Approximationsergebnisse zurückgeben
        return dic_temp
    
    #Methode iterierter Hillclimber. Ruft mit Algorithmusparametern (Schrittweite, Anzahl Hillclimber) eine gewisse
    #Anzahl von Hillclimbern auf. Nimmt als Input Max iterationen bzw. einen Max Iterationen Richtwert. 
    #Die Hillclimber werden mit berechneten max. Iterationen aufgerufen. Bsp: Iterationsrichtwert 450, Anzahl Hillclimber 10
    #45/10 =4.5 -> gerundet 5, also werden maximal 10*5 also 50 Iterationen durchgeführt. 
    #Gibt ein Dictionary mit zu speichernden Approximationsergebnissen zurück
    def it_Hillclimber(self, it_Richtwert):
        #Beim iterierten Hillclimber werden nur zufällig initialisierte Hillclimber genutzt.
        self.algo_params["Initialisierung"]="Zufall"
        #Erster Hillclimber wird durchgeführt und die Approximationsergebnisse als Temporäres Dictionary gespeichert.
        dic_temp=self.Hillclimber(int(np.round(it_Richtwert/self.algo_params["anz_Hillclimber"])))
        #Nun werden n-1 weitere Hillclimber ausgeführt.
        for hillclimber in range(self.algo_params["anz_Hillclimber"]-1):
            #Ergebnisse der Approximation der Iteration werden als Dictionary gespeichert
            dic_it=self.Hillclimber(int(np.round(it_Richtwert/self.algo_params["anz_Hillclimber"])))
            #Ist der Fehler der aktuelle Approximation niedriger als die bisherige Beste..
            if dic_it["fehler"]<dic_temp["fehler"]:
                #Bessere Ergebnisse überschreiben vorherige besten Ergebnisse. Vorher Anzahl Aufrufe und Iterationen
                #hinzu addieren
                dic_it["anz_aufrufe_fehlerfunktion"]+=dic_temp["anz_aufrufe_fehlerfunktion"]
                dic_it["anz_iterationen"]+=dic_temp["anz_iterationen"]
                dic_temp=dic_it
            else:
                #Anzahl Aufrufe Fehlerfunktion, um die der aktuellen Iteration erhöhen
                dic_temp["anz_aufrufe_fehlerfunktion"]+=dic_it["anz_aufrufe_fehlerfunktion"]
                #Anzahl Iterationen, um die der aktuellen Iteration erhöhen
                dic_temp["anz_iterationen"]+=dic_it["anz_iterationen"]
        #Dictionary mit finalen Approximations Ergebnissen zurückgeben
        return dic_temp
    
    #Methode Hillclimber Algorithmus. Nimmt als Input Argument maximale Iterationen. Führt solange den Algorithmus durch,
    #bis die nächste Iteration kein besseres liefert. Gibt ein Dictionary mit Approximationsergebnissen zurück
    def Hillclimber(self, max_it):
        #Erzeugt eine Liste mit den Werten Schrittweite,0,-Schrittweite
        Schritt_Liste=[self.algo_params["Schrittweite"],0,-self.algo_params["Schrittweite"]]
        #Erzeugt eine Matrix mit allen möglichen Veränderungen bei der Anzahl von Parametern.
        #Beispiel: Schrittweite 1, Anzahl Parameter 3 
        # 1 1 1
        # 1 1 0
        # 1 1 -1
        #...
        Schritt_matrix=np.array(list(product(*[Schritt_Liste for x in range(self.anzahl_params)])))
        #Temporäres Dictionary deklarieren. Fehler zunächst auf unendlich setzen um eine Iteration zu gewährleisten.
        dic_temp={"fehler":np.inf}
        #Initial Parameter in Abhängigkeit des ausgewählten Modus setzen
        #Bei Ursprung werden die Parameter alle auf 0 gesetzt
        if self.algo_params["Initialisierung"]=="Ursprung":
            dic_temp["Params_Liste"]=np.array([0 for x in range(self.anzahl_params)])
        #Bei Zufall werden alle Parameter zufällig im Bereich -Schrittweite*max_Iterationen/2 und Schrittweite*max_Iterationen/2
        #gesetzt
        elif self.algo_params["Initialisierung"]=="Zufall":
            dic_temp["Params_Liste"]=np.array([np.random.uniform(-1,1)*self.algo_params["Schrittweite"]*max_it/2 for x in range(self.anzahl_params)])
        #Bei Startwert werden die Initialparameter mit einem übergebenem Startwert gesetzt. Wird momentan aus Usability gründen
        #vom Front-End nicht genutzt.
        elif self.algo_params["Initialisierung"]=="Startwert":
            dic_temp["Params_Liste"]=np.array(self.algo_params["Startwert"])
        #Anzahl Aufrufe Fehlerfunktion mit 0 initialisieren
        dic_temp["anz_aufrufe_fehlerfunktion"]=0
        #Anzahl Iterationen mit 0 initialisieren
        dic_temp["anz_iterationen"]=0
        #Iterieren des Hillclimbers starten, maximal max Iterationen mal iterieren.
        for it in range(max_it):
            #Temporäre Matrix wird mit aktuellen Parametern(Position) und der Schritt Matrix erzeugt.
            temp_matrix=Schritt_matrix+dic_temp["Params_Liste"]
            #Für alle Parameter Möglichkeiten werden Y-Werte erzeugt. Parallelisiert durch Matrixberechnungen
            array_y_Werte=np.apply_along_axis(self.y_Polynome_erstellen, axis=1, arr=temp_matrix)
            #Fehlerfunktion wird mit der erzeugten Matrix. Fehler, der Index der besten Parameter im Y-Array und der Fehler
            #in Abhängigkeit von x wird zurückgegeben
            fehler_it, index_params, fehler_array_it=self.berechne_fehler(array_y_Werte)
            #Inkrementierung der Anzahl der Fehleraufrufe, um die Anzahl der Parametermöglichkeiten, die untersucht wurden.
            dic_temp["anz_aufrufe_fehlerfunktion"]+=len(temp_matrix)
            #Inkrementierung der Iterationen um 1
            dic_temp["anz_iterationen"]+=1
            #Wenn Fehler kleiner ist, als der aktuelle Fehler, dann Dictionary überschreiben, ansonsten Iterationen beenden
            if fehler_it<dic_temp["fehler"]:
                dic_temp["Params_Liste"]=temp_matrix[index_params]
                dic_temp["fehler"]=fehler_it
                dic_temp["fehler_array"]=fehler_array_it
                dic_temp["y_array"]=array_y_Werte[index_params]
            else:
                break
        #Rückgabe der finalen Approximationsergebnisse
        return dic_temp
     
    #Methode Rastersuche. Wird mit einem Rasterrichtwert aufgerufen (momentan 100000). Dieser Richtwert gibt an,
    #wieviele Elemente das Raster beinhalten soll. Mindestens den Rasterrichtwert, höchstens aber die nächst mögliche Anzahl
    #Beispiel: Rasterrichtwert 10, Anzahl Parameter 3
    #Dritte Wurzel aus 10 ist 2,xxxx
    #Aufgerundet 3
    #3*3*3=27
    #Es werden als 27 Elemente (3x3x3 Möglichkeiten) erzeugt.
    #Gibt die Approximationsergebnisse zurück
    def Rastersuche(self, Rasterrichtwert):
        #Umrechnung des Rasterrichtwerts. s.o.
        Rasterrichtwert=np.ceil(Rasterrichtwert**(1/self.anzahl_params))
        #Berechnung der Schrittweite des Rasters aus dem Rasterrichtwert.
        self.algo_params["step"]=(self.algo_params["max"]-self.algo_params["min"])/(Rasterrichtwert-1)
        #Erzeugung einer Liste mit den verschiedenen Möglichkeiten für einen Parameter
        list_values=[round(x,9) for x in np.arange(self.algo_params["min"],self.algo_params["max"]+self.algo_params["step"],self.algo_params["step"])]
        #Erzeugung einer Liste mit den verschiedenen Möglichkeiten für alle Parameter aus den Möglichkeiten für einen Parameter
        temp_matrix=np.array(list(product(*[list_values for x in range(self.anzahl_params)])))
        #Y-Werte für alle Parameter Möglichkeiten berechnen
        array_y_Werte=np.apply_along_axis(self.y_Polynome_erstellen, axis=1, arr=temp_matrix)
        #dic Temp deklarieren
        dic_temp={}
        #Fehlerfunktion wird mit der erzeugten Matrix. Fehler, der Index der besten Parameter im Y-Array und der Fehler
        #in Abhängigkeit von x wird zurückgegeben 
        dic_temp["fehler"], index_params, dic_temp["fehler_array"]=self.berechne_fehler(array_y_Werte)
        #Besten Parameter aus Parametermatrix auswählen
        dic_temp["Params_Liste"]=temp_matrix[index_params]
        #Y Werte für besten Parameter aus Y-Werte Matrix auswählen
        dic_temp["y_array"]=array_y_Werte[index_params]
        #Anzahl Aufrufe Fehlerfunktion entspricht dem Rasterrichtwert hoch der Anzahl der Parameter (Rückrechnung)
        dic_temp["anz_aufrufe_fehlerfunktion"]=Rasterrichtwert**self.anzahl_params
        #Iterationen sind immer 1. Die Rastersuche berechnet parallelisiert mit Matrixfunktionen ihre Ergebnisse.
        dic_temp["anz_iterationen"]=1
        #Approximationsergebnisse zurückgeben
        return dic_temp
    #Methode zur Berechnung der Y-Werte von Polynomfunktion(en). Nimmt als Input eine Matrix aus Funktionsparameternmöglichkeiten.
    #Gibt eine Matrix mit Y-Werten für eingegebene Funktionsparameter zurück.
    def y_Polynome_erstellen(self, params_array):
        #Erzeugt zunächst eine Matrix mit Y-Werte für alle Bestandteile des Polynoms. Dieses wird mit den Parametern (Faktoren)
        #multipliziert und dann aufsummiert
        #Es resultiert eine Matrix in der die Zeilen Y-Werten für Polynome entsprechend. Mit einer Anzahl von Zeilen gleich
        #der Anzahl der übergebenen Funktionsparametermöglichkeiten.
        return np.sum(np.power(self.x_tabellen[:,np.newaxis],self.power_array)*params_array, axis=1)
    
    #Ausführmethode zur Berechnung des Fehlers. Wird mit einem Array von Y-Werten aufgerufen. Führt in Abhängigkeit
    #der ausgewählten Optimierungsfuntkion entweder L1(punktweiser maximaler Abstand) oder L2 (mittlerer quadratischer Abstand)
    #durch und gibt die Ergebnisse zurück
    def berechne_fehler(self, input_array):
        #Differenz von Y-Werten und Sinus Y-Werten bilden
        dif_array=input_array-self.sin_y
        #Wenn L1 maximaler punktweiser Abstand berechnen, ansonsten mittlerer quadratischer Abstand berechnen.
        if self.auswahl_fehlerfunktion=="L1":
            return self.maximaler_punktweiser_Abstand(dif_array)
        elif self.auswahl_fehlerfunktion=="L2":
            return self.mittlerer_quadratischer_Abstand(dif_array)
        
    #Methode zur Berechnung des maximimalen punktweisen Abstands. Nimmt Einen Array mit der Differenz aus Approximation
    #Y-Werten und Sin Y Werten entgegen. Berechnet den absoluten Abstand und daraus das Maximum.
    #Der Minimale Fehler wird zurückgegeben, der Index für die Funktionsparameter mit dem niedrigsten Fehler auch
    #und ebenfalls der Array mit den entsprechenden absoluten Fehlern für die X-Werte.
    def maximaler_punktweiser_Abstand(self, array_in):
        array_in=abs(array_in)
        fehler=np.min(np.max(array_in, axis=1))
        index_beste_params=np.argmin(np.max(array_in, axis=1))
        fehler_array=array_in[index_beste_params]
        return fehler, index_beste_params, fehler_array
    
    #Methode zur Berechnung des mittleren quadratischen Abstands. Nimmt Einen Array mit der Differenz aus Approximation
    #Y-Werten und Sin Y Werten entgegen. Berechnet den quadratischen Abstand und daraus das Mittel.
    #Der Minimale Fehler wird zurückgegeben, der Index für die Funktionsparameter mit dem niedrigsten Fehler auch
    #und ebenfalls der Array mit den entsprechenden absoluten Fehlern für die X-Werte.
    def mittlerer_quadratischer_Abstand(self, array_in):
        array_in=np.power(array_in, 2)
        fehler=np.min(np.mean(array_in, axis=1))
        index_beste_params=np.argmin(np.mean(array_in, axis=1))
        fehler_array=array_in[index_beste_params]
        return fehler, index_beste_params, fehler_array
#Funktion die Extern zur Approximation aufgerufen wird. Ist nicht teil der Klasse Approximierer! Ist aber im selben
#Modul (Backend) enthalten.
def approximieren(algorithmus, fehlerfunktion, algo_params_dic,  polynomgrad):
    #Timetracking starten, jetzigen Zeitpunkt messen
    start_time = time.time()
    #Approximierer instanziieren
    calc=Approximierer(algorithmus, fehlerfunktion, algo_params_dic, polynomgrad)
    #Approximation durchführen
    calc.algorithmus_ausführen()
    #Ausführungszeit berechnen, jetzige Zeit minus Startzeit
    ausführungszeit=time.time() - start_time
    return calc.Params, calc.fehler,calc.Tabelle,calc.anz_aufrufe_fehlerfunktion,calc.anz_iterationen, ausführungszeit