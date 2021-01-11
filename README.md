# Portfolio Manager

Mithilfe von Spielgeld lassen sich Aktien kaufen,
verwalten und schließlich wieder verkaufen.
Alle Aktien lassen sich außerdem darstellen.

## Installation

Vorausgesetzt ist eine aktuelle Python 3 Version. 
Alle benötigten Librarys können wie folgt installiert werden:
~~~~bash
pip install -m requirements.txt
~~~~

### Dependencys
Bei dem hier vorliegenden Repository handelt es sich um das Frontend des Programmes. 
Als Backend läuft eine Rest-API auf einem Heroku Server. Dieser kommuniziert mit einer MySQL Datenbank.

## Bedienung

Wird das Programm erstmalig geöffnet, erscheint eine Registerkarte. 
Hier muss sich der Nutzer mit einem Username sowie Passwort registrieren. Die Eingabe kann mithilfe der Enter Taste bestätigt werden.
Die Login-Daten haben später für den Nutzer keine weitere Bedeutung.

Nach der Registrierung öffnet sich nun das Hauptfenster.
Hier befindet sich eine Tabelle mit allen Aktien des Nutzers, sowie einem Graph, welcher eine ausgewählte Aktie anzeigt.
Die dargestellte Aktie kann durch Anklicken einer Aktie in der Tabelle geändert werden.
Mithilfe des „Sell“-Knopfes öffnet sich ein Frage-Dialog. Hier kann die Anzahl der zu verkaufenden Aktien gewählt und anschließend bestätigt werden.

In der oberen rechten Ecke befindet sich ein Textfeld. Durch Eingabe und bestätigen mittels der Enter-Taste, wird nach einer neuen Aktie gesucht.

![Portfolio](./doc/portfolio_page.png)

Daraufhin wird der Nutzer zu einer detaillierteren Ansicht der Aktie weitergeleitet. 
Diese kann nun über den „Buy“-Knopf gekauft werden, wobei ebenfalls zuerst die Anzahl ausgewählt werden muss.

Mithilfe der „Back to Portfolio“-Taste gelangt der Nutzer zurück zu seinem Portfolio.

## Aufgabe der Python Files

## `controller.py`

Der Controller steuert das gesamte Programm und beinhaltet die Programmlogik.
Mithilfe von PyQt Signals bekommt er ausgelöste Events von der View mit.
~~~~Python
    def init_me(self):
        self._register.enter_pressed.connect(self.do_register)
        self._main_gui.signal_table_clicked.connect(self.clicked_table)
        self._main_gui.signal_buy_holding.connect(self.buy_holding)
        self._main_gui.signal_sell_holding.connect(self.sell_holding)
        self._main_gui.signal_change_to_portfolio.connect(self.change_card_to_portfolio)
        self._main_gui.signal_change_to_browse_holdings.connect(self.change_card_to_browse_holdings)
        self._main_gui.signal_browse_new_holding.connect(self.browse_new_holding)
        self._main_gui.signal_period_max.connect(self.change_period)
        self._main_gui.signal_period_year.connect(self.change_period)
        self._main_gui.signal_period_month.connect(self.change_period)
~~~~


## `view.py`

Die View ist für die Darstellung der Daten zuständig.
Sie wurde mithilfe von PyQt5 und pyqtgraph erstellt.
Wie für PyQt üblich ist sie ebenfalls Objektorientiert programmiert.
~~~~Python
def __init__(self, size):
~~~~
Im Konstruktor werden zuerst alle Objektvariablen und Widgets für die Darstellung erstellt.
Anpassungen zu diesen finden anschließlich in den zugehörigen inits statt: 
~~~~Python
init_portfolio
init_browse_holdings
init_table
~~~~
Mithilfe von PyQt Signals und Events leitet sie Nutzereingaben an den Controller weiter, welcher diese anschließend verarbeitet
~~~~Python
enter_pressed = pyqtSignal()
self.textbox_password.returnPressed.connect(self.enter_pressed)
~~~~
## `model.py`

Das Model beinhaltet die Funktionen für die Datenbankabfragen.
~~~~Python
environment = os.environ.get('ENVIRON', 'development')
with open("config.yaml", "r") as yamlfile:
    self.cfg = yaml.load(yamlfile, Loader=yaml.FullLoader)

self.api_host = self.cfg[environment]['api_endpoint']
~~~~
Aus der config.yaml Datei wird der zugehörige api_host geladen. Dieser lässt sich wie folgt, zwischen Entwicklung auf dem Server und lokaler Entwicklung wächseln: 
~~~~Bash
export ENVIRON=production
~~~~
oder
~~~~Bash
export ENVIRON=development
~~~~
## `hashcode_utils.py`

Hier befinden sich die Hilfsfunktionen für den Hashcode. 
Der Hashcode wird in der `token.txt` Datei abgespeichert. 

## `holdings_data_utils.py`

Hier befinden sich die Hilfsfunktionen für die Abfragen der Aktiendaten.
Die Daten werden wie in `model.py` von einer Rest-API abgefragt. 
Dies geschieht über die Library yfinance.

### Frontend total lines of Code
870

## Links 
GUI: [Qt5 Doku](https://doc.qt.io/qtforpython/) - [Pyqtgraph Doku](https://pyqtgraph.readthedocs.io/en/latest/)

Requests: [Requests Doku](https://requests.readthedocs.io/de/latest/)


