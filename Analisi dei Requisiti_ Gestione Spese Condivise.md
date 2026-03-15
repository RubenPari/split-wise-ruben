# **Analisi dei Requisiti: Progetto "Split-Wise-Ruben"**

Questo documento delinea le specifiche funzionali e tecniche per un app mobile dedicata alla gestione e suddivisione delle spese tra gruppi di utenti amici

## **1\. Obiettivi del Progetto**

Creare un'applicazione che semplifichi la tracciabilità dei debiti e crediti all'interno di un gruppo, automatizzando il calcolo dei saldi e riducendo al minimo il numero di transazioni necessarie per "pareggiare i conti".

## **2\. Requisiti Funzionali**

### **2.1 Gestione Utente (Auth)**

* **Registrazione/Login:** Accesso tramite email/password o OAuth (Google).  
* **Profilo:** Modifica di nome, avatar e valuta preferita.  
* **Ricerca:** Possibilità di trovare altri utenti tramite email per aggiungerli ai gruppi.

### **2.2 Gestione Gruppi**

* **Creazione Gruppo:** Un utente può creare un gruppo (es. "Viaggio a Parigi") e invitare membri.  
* **Gestione Membri:** Aggiunta o rimozione di partecipanti (solo se non hanno debiti pendenti).  
* **Categorie:** Ogni gruppo può avere categorie di spesa personalizzate (Cibo, Affitto, Trasporti).

### **2.3 Gestione Spese**

* **Inserimento Spesa:**  
  * Titolo, importo e data.  
  * Selezione di chi ha pagato (singolo o più persone).  
  * Selezione di come dividere (parti uguali, percentuali, quote fisse).  
* **Allegati:** Possibilità di caricare la foto di uno scontrino.  
* **Storico:** Cronologia delle attività del gruppo (chi ha aggiunto cosa).

### **2.4 Logica di Bilanciamento (Core)**

* **Calcolo Saldi:** Visualizzazione immediata di quanto l'utente deve o deve ricevere nel gruppo.  
* **Algoritmo di Semplificazione:** Implementazione di una logica per minimizzare le transazioni (es: se A deve 10 a B e B deve 10 a C, il sistema suggerisce che A paghi direttamente C).  
* **Salda Conto:** Funzionalità per segnare un debito come pagato.

## **Stack Tecnologico**

* **Frontend:** React native typescript  
* **Backend:** fastapi python  
* **Database:** MySQL