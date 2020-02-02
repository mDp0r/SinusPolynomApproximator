#Import benötigter Module des Frontends sowie Import des Backends
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash
import pandas as pd
from dash.dependencies import Input, Output, State
import Backend

#Erstellung einer Dash Applikationsklasse
app = dash.Dash(__name__)
#Definition des Layouts
app.layout = html.Div([
    #Anlegen der Auswahlreiter für die implementierten Algorithmen
    dcc.Tabs([
    #Reiter Rastersuche 
    dcc.Tab(value="Rastersuche",label='Rastersuche', children=[ 
        #HTML Objekt Input Rasteranfang bestehend aus Label und Inputfeld
        html.Div(
        (html.Label('Rasteranfang'),
        dcc.Input(id="RAS_a",placeholder='𝑛',value='', type='number', style={"width":150}, required=True)),
        style={ 'display':'inline-block'}),
        #HTML Objekt Input Rasterende bestehend aus Label und Inputfeld
        html.Div(
        (html.Label('Rasterende'),
        dcc.Input(id="RAS_e",placeholder='𝑚 ; 𝑚 > 𝑛',value='', type='number', style={"width":150}, required=True)),
        style={ 'display':'inline-block'}),
    ]),
    ##Bedingung m>n müsste noch geprüft werden, aber wie? Eventuell in Callback oder in Backend "if n > m: n, m = m, n"
    #Reiter Hillclimber
    dcc.Tab(value="Hillclimber",label='Hillclimber', children=[
        #HTML Objekt Input Schrittweite bestehend aus Label und Inputfeld
        html.Div(
        (html.Label('Schrittweite'),
        dcc.Input(id="HC_step",placeholder='𝑛 > 0',value='', type='number', min=0.000000001, style={"width":150}, required=True)),
        style={ 'display':'inline-block'}),
        
        #Auswahl ob Parameter im Ursprung (0) oder zufällig gewählt
        html.Div(
        (dcc.RadioItems(id="HC_init",
        options=[
        {'label': 'Ursprung', 'value': 'Ursprung'},
        {'label': 'Zufall   | Startposition', 'value': 'Zufall'},
    ],
        labelStyle={'display':'inline-block'},
        value="Ursprung")),
        style={ 'display':'inline-block'})
    ]),
 
    #Reiter iterierter Hillclimber   
    dcc.Tab(value="it_Hillclimber",label='Iterierter Hillclimber', children=[
        #HTML Objekt Input Anzahl Iterationen bestehend aus Label und Inputfeld
        html.Div(
        (html.Label('Anzahl Iterationen'),
        dcc.Input(id="IHC_i",placeholder='0 < 𝑛 ≤ 10',value='', type='number', min=1, max=10, step=1, style={"width":150}, required=True)),
        style={ 'display':'inline-block'}),
        #HTML Objekt Input Schrittweite bestehend aus Label und Inputfeld
        html.Div(
        (html.Label('Schrittweite'),
        dcc.Input(id="IHC_step",placeholder='𝑛 > 0',value='', type='number', min=0.000000001, style={"width":150}, required=True)),
        style={ 'display':'inline-block'}),
    ]),
    
    #Reiter Hooke & Jeeves
    dcc.Tab(value="HAJ",label='Hooke & Jeeves', children=[
        #HTML Objekt Input Schrittweite bestehend aus Label und Inputfeld
        html.Div(
        (html.Label('Schrittweite'),
        dcc.Input(id="HAJ_step",placeholder='𝑛 > 0',value='', type='number', min=0.000000001, style={"width":150}, required=True)),
        style={ 'display':'inline-block'})
      
    ])
            #Vorauswahl des Tabs Rastersuche
            ], id="Algo_Tabs",value="Rastersuche"),
    
    #HTML Elemente zur Auswahl von Fehlerfunktion, Polynomgrad, Zu Approximierende Funktion, Intervall Anfang
    #und Intervallende sowie Button zur Ausführung der Approximation
    html.Div([
    html.Div([    
    html.Div([
    html.Label('Fehlerfunktion'),
    dcc.RadioItems(id="Fehlerfunktion",
    options=[
        {'label': 'Max. punktweiser Abstand', 'value': 'L1'},
        {'label': 'Mittl. quadratischer Abstand', 'value': 'L2'},
    ],
        labelStyle={'display':'inline-block'}, value="L1")]),
    
    html.Div(
    [html.Label('Polynomgrad'), dcc.Input(id="poly", placeholder='−1 ≤ 𝑛 ≤ 6',value='', type='number', min=-1, max=6, step=1, style={"width":125}, required=True)],
    style={ 'display':'inline-block'}),
    
    html.Div(
    [html.Label('Funktion'), dcc.Input(id="func_aprox",value='',type="text", style={"width":125}, required=True)],
    style={ 'display':'inline-block'}),
        
    html.Div(
    [html.Label('Intervall Anfang'), dcc.Input(id="min_intervall",value='', type="number",style={"width":125}, required=True)],
    style={ 'display':'inline-block'}),   
        
    html.Div(
    [html.Label('Intervall Ende'), dcc.Input(id="max_intervall",value='',type="number", style={"width":125}, required=True)],
    style={ 'display':'inline-block'}),
    
    html.Div(
    html.Button('Approximieren!', id='button'), style={ 'display':'inline-block'})
    
    ], style={ 'display':'inline-block', "width":"49%"}),
    
    #HTML Objekt zur Ausgabe von Funktionsparametern, Fehler, Anzahl der Aufrufe der Fehlerfunktion, Iterationen und Laufzeit
    html.Div(id="Text_Out",style={ 'display':'inline-block', "width":"49%"})
    ]),
    
    #HTML Objekt für die Ausgabe der beiden Visualisierungen
    html.Div([
    html.Div(dcc.Graph(id='Funktionen_Graph'),style={ 'display':'inline-block', "width":"49%"}),
    html.Div(dcc.Graph(id='Fehler_Graph'),style={ 'display':'inline-block', "width":"49%"})   
    ]),
    
    #Unsichtbare HTML-Felder in denen die Approximationsergebnisse zwischengespeichert werden
    html.Div(id="store_Funktionsparameter",style={"display":"none"}),
    html.Div(id="store_Fehler",style={"display":"none"}),
    html.Div(id="store_Tabelle",style={"display":"none"}),
    html.Div(id="store_Anzahl_Aufrufe",style={"display":"none"}),
    html.Div(id="store_Anzahl_Iterationen",style={"display":"none"}),
    html.Div(id="store_Laufzeit",style={"display":"none"})
])

#Callback zur Ausführung der Approximation durch das Backend und Zwischenspeicherung in Hidden Div Feldern.
#Zunächst Definition des Callback Layouts
#Output:Alle Zwischenspeicher Felder
#Input: Button (Click löst Approximation aus)
#State: Zusätzliche Informationen, die aus Inputfeldern abgefragt werden. Werden für die Approximation benötigt.
@app.callback(
    [
        Output("store_Funktionsparameter", "children"),
        Output("store_Fehler", "children"),
        Output("store_Tabelle", "children"),
        Output("store_Anzahl_Aufrufe", "children"),
        Output("store_Anzahl_Iterationen", "children"),
        Output("store_Laufzeit", "children")
    ],
    [Input("button", 'n_clicks')],
    [State("Algo_Tabs", "value"), 
     State("poly","value"),
     State("Fehlerfunktion","value"),
     State("RAS_a", "value"),
     State("RAS_e", "value"),
     State("HC_init", "value"),
     State("HC_step", "value"),
     State("IHC_i", "value"),
     State("IHC_step", "value"),
     #####
     State("HAJ_step","value"),
     #####
     State("func_aprox","value"),
     State("min_intervall","value"),
     State("max_intervall","value")
    ]   
)
#Funktion, wie die Aktualisierung stattfinden soll. Nimmt die Anzahl der Clicks des Buttons und die Werte in allen
#Inputfeldern entgegen.
def callback_func(n_clicks, Algorithmus, polynomgrad, fehlerfunktion,Ras_Min, Ras_Max,
                  Initialisierung_HC, Schrittweite_HC, Iterationen_IHC, Schrittweite_IHC, Schrittweite_HAJ,
                 math_eq_string, min_intervall, max_intervall):
    #Wenn der Button geclickt wurde...
    if n_clicks is not None:
        #Rastersuche Parameter setzen, wenn Rastersuche ausgewählt
        if Algorithmus=="Rastersuche":
            #Überprüfung ob Min kleiner Max, wenn nicht, tauschen. Wenn gleich im Bereich Eingabe-1 und Eingabe
            #(Exception Handling)
            if Ras_Min<Ras_Max:
                algo_params={"min":Ras_Min,"max":Ras_Max }
            elif Ras_Max<Ras_Min:
                algo_params={"min":Ras_Max,"max":Ras_Min}
            else:
                algo_params={"min":(Ras_Max-1),"max":Ras_Max }
        #Hillclimber Parameter setzen, wenn Hillclimber ausgewählt
        elif Algorithmus=="Hillclimber":
            algo_params={"Schrittweite":Schrittweite_HC,"Initialisierung":Initialisierung_HC}
        #iterierter Hillclimber Parameter setzen, wenn iterierter Hillclimber ausgewählt
        elif Algorithmus=="it_Hillclimber":
            algo_params={"anz_Hillclimber":Iterationen_IHC, "Schrittweite":Schrittweite_IHC}
            #####
        #Hooke and Jeeves Parameter setzen, wenn Hooke and Jeeves ausgewählt
        elif Algorithmus=="HAJ":
            algo_params={"Schrittweite":Schrittweite_HAJ}
            #####
        #Approximation durchführen
        return Backend.approximieren(Algorithmus, fehlerfunktion, algo_params, polynomgrad,min_intervall, max_intervall, math_eq_string) 
    else:
        #Falls Button nicht geclickt wurde, kein Update durchführen.
        return (dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update)

#Callback für die Ausgabe im Textfeld. 
#Zunächst Definition des Callback Layouts:
#Output ist das Textfeld, Input versteckte Zwischenspeicher Felder
@app.callback(
    Output("Text_Out", "children"),
    [Input("store_Funktionsparameter", "children"),
    Input("store_Fehler", "children"),
    Input("store_Anzahl_Aufrufe", "children"),
    Input("store_Anzahl_Iterationen", "children"),
    Input("store_Laufzeit", "children") ])

#Funktion zur Textausgabe der Approximationsparameter. Nimmt als Input versteckte Zwischenspeicher Felder.
def Textausgabe(params, fehler, anz_aufrufe, anz_it, laufzeit):
    #Falls bereits eine Approximation durchgeführt wurde..
    if params is not None:
        #Output String erstellen
        Output_String=("Funktionsparameter: {} | Fehler: {} | Aufrufe Fehlerfunktion: {} | Iterationen: {} | Laufzeit: {}s").format(
        params, fehler, anz_aufrufe, anz_it, laufzeit)
        #Ausgabe der Approximationsergebnisse als Text
        return Output_String
    else:
        #Falls noch keine Approximation durchgeführt wurde, kein Update durchführen.
        return dash.no_update
    
#Callback zur Aktualiesierung der ersten Grafik (beinhaltet Approximation und zu approximierende Funktion)
#Zunächst Definition des Callback Layouts:
#Input ist die zwischengespeicherte Tabelle aus der Approximation
#Output ist die Visualisierung (Funktionen_Graph)
@app.callback(
    Output("Funktionen_Graph", "figure"),
    [Input("store_Tabelle", "children")]
)

#Funktion zur Aktualisierung der ersten Visualisierung
def update_Funktionen(Tabelle_json):
    #Wenn bereits eine Approximierung durchgeführt wurde,..
    if Tabelle_json is not None:
        #JSON String in Pandas DataFrame konvertieren
        Tabelle=pd.read_json(Tabelle_json, orient="split")
        #Visualisierung Updaten
        return {"data":[go.Scatter(x=Tabelle["x"], y=Tabelle["aprox_y"], mode='lines', name="Funktion", text="zu approximierende Funktion"),
                       go.Scatter(x=Tabelle["x"], y=Tabelle["polynom_y"], mode='lines', name="Polynom", text="Polynom+Schnittfläche",fill="tonexty")]}
    else:
        #Falls noch keine Approximation durchgeführt wurde, kein Update durchführen
        return dash.no_update
    
#Callback zur Aktualiesierung der zweiten Grafik (beinhaltet Fehler in Abhängigkeit von x, Mittel und Max)
#Zunächst Definition des Callback Layouts:
#Input ist die zwischengespeicherte Tabelle aus der Approximation
#Output ist die Visualisierung (Fehler_Graph)
@app.callback(
    Output("Fehler_Graph", "figure"),
    [Input("store_Tabelle", "children")]
)
#Funktion zur Aktualisierung der zweiten Visualisierung
def update_Fehler(Tabelle_json):
    #Wenn bereits eine Approximierung durchgeführt wurde,..
    if Tabelle_json is not None:
        #JSON String in Pandas DataFrame konvertieren
        Tabelle=pd.read_json(Tabelle_json, orient="split")
        #Durchschnittlichen Fehler als neuer Spalte in der Tabelle erzeugen.
        Tabelle["mean_fehler"]=Tabelle["fehler"].mean()
        #Visualisierung updaten
        return {"data":[go.Scatter(x=Tabelle["x"], y=Tabelle["fehler"], name="Fehler", text="Fehler",mode="lines",marker_color='purple'),
go.Scatter(x=Tabelle["x"], y=Tabelle["mean_fehler"], name="Durchschnitt Fehler", text="Durchschnitt",mode="lines",marker_color='orange'),
go.Scatter(x=[Tabelle.set_index("x")["fehler"].idxmax()], y=[Tabelle["fehler"].max()], name="Max. Fehler", text="Max", mode="markers", marker_size=7, marker_color="red")
]}
    else:
        #Falls noch keine Approximation durchgeführt wurde, kein Update durchführen
        return dash.no_update
    
#Lokalen Appserver starten.
if __name__ == '__main__':
    app.run_server()    