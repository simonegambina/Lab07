import flet as ft

from UI.view import View
from model.model import Model

# Prende i dati definitivi dal model e e li stampa tramite il view
class Controller:
    def __init__(self, view: View, model: Model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model
        # other attributes
        self._mese = 0

    # La funzione che chiama il bottone "Umidità media" del view
    def handle_umidita_media(self, e):

        # primo filtro
        if self._mese == 0:
            self._view.create_alert("Selezionare un mese:")
            return

        self._view.lst_result.controls.clear()

        # dati presi dal model
        medie = self._model.get_umidita_media(self._mese)

        self._view.lst_result.controls.append(
            ft.Text("L'umidità media nel mese selezionato è:")
        )
        self._view.lst_result.controls.append(ft.Text(""))

        for localita in sorted(medie.keys()):
            self._view.lst_result.controls.append(
                ft.Text(f"{localita}: {medie[localita]:.4f}")
            )

        self._view.update_page()

    # La funzione che chiama il bottone "Calcola sequenza" del view
    def handle_sequenza(self, e):

        # primo filtro
        if self._mese == 0:
            self._view.create_alert("Selezionare un mese:")
            return

        self._view.lst_result.controls.clear()

        # dati presi dal model
        best_path, best_cost = self._model.calcola_sequenza_ottima(self._mese)

        self._view.lst_result.controls.append(
            ft.Text(f"La sequenza ottima ha costo: {best_cost} ed è:")
        )
        self._view.lst_result.controls.append(ft.Text(""))

        for situazione in best_path:
            self._view.lst_result.controls.append(ft.Text(str(situazione)))

        self._view.update_page()

    # lettura del mese
    def read_mese(self, e):
        self._mese = int(e.control.value)

