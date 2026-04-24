from database.meteo_dao import MeteoDao

# Prende i dati puliti dal DAO e li filtra ancora di più per darli al controller
class Model:

    def __init__(self):

        # prende dal DAO le situazioni meteo provenienti dal database
        self._situazioni = MeteoDao.get_all_situazioni()
        self._best_path = []  # crea una lista vuota dove inserire la miglior sequenza
        self._best_cost = float("inf")
        self._situazioni_mese = {}
        self._localita = sorted({s.localita for s in self._situazioni})

    def get_umidita_media(self, mese):
        somme = {}
        conteggi = {}

        for s in self._situazioni:
            if s.data.month == mese:
                somme[s.localita] = somme.get(s.localita, 0) + s.umidita
                conteggi[s.localita] = conteggi.get(s.localita, 0) + 1

        medie = {}
        for localita in somme:
            medie[localita] = somme[localita] / conteggi[localita]

        return medie

    # calcolo della migliore sequenza col metodo della ricorsione
    def calcola_sequenza_ottima(self, mese):

        self._best_path = []
        self._best_cost = float("inf")
        self._situazioni_mese = self._get_situazioni_primi_15_giorni(mese)

        parziale = []
        conteggi = {localita: 0 for localita in self._localita}

        # il metodo ricorsivo trova la migliore lista e ne restituisce i valori
        # per poi ciclare su se stesso finché non trova altri valori migliori
        self._ricorsione(1, parziale, 0, conteggi)

        # restituisce i valori per passarli al controller
        return self._best_path, self._best_cost

    # salva le situazioni di solo 15 giorni
    def _get_situazioni_primi_15_giorni(self, mese):
        diz = {}

        for s in self._situazioni:

            # filtro: n.giorni = 15
            if s.data.month == mese and 1 <= s.data.day <= 15:
                if s.data.day not in diz:
                    diz[s.data.day] = []
                diz[s.data.day].append(s)

        for giorno in diz:
            diz[giorno].sort(key=lambda x: x.localita)

        return diz

    # Metodo ricorsivo
    def _ricorsione(self, giorno, parziale, costo_parziale, conteggi):

        # caso terminale: controlla se il giorno è 16, così da chiudere una prima sequenza.
        if giorno == 16:
            if costo_parziale < self._best_cost:
                self._best_cost = costo_parziale
                self._best_path = list(parziale)
            return

       # caso ricorsivo: prende il numero del giorno
        for situazione in self._situazioni_mese[giorno]:

            # e controlla se la sequenza rispetta i vincoli
            if self._is_ammissibile(situazione, parziale, conteggi):

               #se lo è la aggiunge alla lista parziale e aggiorna il numero dei giorni
                parziale.append(situazione)
                conteggi[situazione.localita] += 1

               # inizializza la variabile costo composta dal valore dell'umidità
                costo_aggiuntivo = situazione.umidita

               # più una somma di 100 per un eventuale trasferta in un'altra città
               # (controlla se la città e diversa -> trasferta)
                if len(parziale) > 1 and parziale[-2].localita != situazione.localita:
                    costo_aggiuntivo += 100

                nuovo_costo = costo_parziale + costo_aggiuntivo

                # se il nuovo costo è minore di quello migliore, ricomincia
                if nuovo_costo < self._best_cost:
                    self._ricorsione(giorno + 1, parziale, nuovo_costo, conteggi)

                # backtracking
                conteggi[situazione.localita] -= 1
                parziale.pop()

    # Filtrazione dati
    def _is_ammissibile(self, situazione, parziale, conteggi):

        # Primo filtro: non puoi stare nella stessa città per più di 6 giorni
        if conteggi[situazione.localita] >= 6:
            return False

        # se la lista è vuota, non sei ancora stato da nessuna parte -> va bene
        if len(parziale) == 0:
            return True

        ultima_localita = parziale[-1].localita

        # controlla i conteggi
        if situazione.localita != ultima_localita:
            consecutivi = self._conta_consecutivi_finale(parziale)

            # prima di cambiare città devono passare minimo 3 giorni
            if consecutivi < 3:
                return False

        return True

    # Conteggio giorni consecutivi nella stessa città
    def _conta_consecutivi_finale(self, parziale):

        # se la lista è vuota, non sei ancora stato da nessuna parte -> va bene e restituisce 0
        if len(parziale) == 0:
            return 0

        ultima_localita = parziale[-1].localita
        count = 0
        i = len(parziale) - 1

        while i >= 0 and parziale[i].localita == ultima_localita:
            count += 1
            i -= 1

        return count



