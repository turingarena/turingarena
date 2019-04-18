# Indovina il numero

##### Problema della Suite di Esempio di TuringArena

Il tuo avversario ha pensato un numero da `1` a `100` e, chiamando la seguente procedura, ti sfida ad indovinarlo:

```
play(100)```

Implementa nella procedura `play(n)` una logica che ti vada ad individuare il numero segreto nel minor numero di tentativi possibile.
Ogni volta che spari una possibile risposta, invocando da `play(n)` la funzione `guess(candidato)`, potrà succedere una delle seguenti tre cose:

+ se `candidato` è proprio il numero pensato dall'avversario allora la partita termina con successo.

+ se `candidato` è maggiore del numero segreto allora la procedura `guess(candidato)` restituisce il valore `1` ed il controllo torna alla procedura `play(n)` che dovrà stabilire come proseguire la partita.

+ situazione del tutto analoga se `candidato` è minore del numero segreto, solo che ora la procedura `guess(candidato)` restituisce il valore `-1`.

Nel progettare la tua logica, lasciati guidare dal criterio del caso peggiore, ossia cerca di ridurre al minimo i tentativi che compirai alla peggio (come ad esempio del caso l'avversario fingesse di avere pensato un numero ma in realtà stesse solo attento a fornire risposte coerenti ma il meno informative possibile).


### Goals

In TuringArena, i goal di un problema sono quegli obiettivi che ti proponiamo di provare a raggiungere.
Non li abbiamo ancora implementati nell'evaluator ma per questo problema i seguenti goal appaiono ben azzeccati:

- `correct`: giungere infine ad indovinare il numero segreto.

- `no-rep`: indovinare il numero segreto evitando di spendere più volte uno stesso guess.

- `51`: quando $n=100$, farsi bastare $51$ guess.

- `quartino`: quando $n=100$, farsi bastare $1+1+25=27$ guess.

- `almost-opt`: regalare massimo un guess più dello stretto necessario.

- `opt`: non regalare nemmeno un guess.


### Ulteriori spiegazioni di valenza generale

Nel file da sottomettere, o sperimentare in locale, devi implementare la procedura `play(n)`. Puoi partire dal file di template per il linguaggio di programmazione da te scelto, purchè tra quelli già supportati da TuringArena (vedi se il comando `turingarena file sync` genera il template per quel linguaggio).
