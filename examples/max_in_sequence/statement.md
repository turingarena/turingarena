# Trova il massimo in una sequenza data

##### Problema della Suite di Esempio di TuringArena

Ricevi in ingresso una sequenza di `n` valori interi indicizzati coi numeri naturali (ossia partendo da `0`) e devi ritornare l'indice di un massimo entro la sequenza.
Un intero `v` è *un massimo* entro un insieme di interi `S` quando $v\geq u$ per ogni $u\in S$.

### Goals

In TuringArena, i goal di un problema sono quegli obiettivi che ti proponiamo di provare a raggiungere.
Per questo problema abbiamo previsto un solo goal:

- `correct`: fornire sempre la risposta corretta, ossia quel numero naturale $i \in [0,n-1)$ tale che `a[i]`$\geq$`a[j]` per ogni $j \in [0,n-1)$.

Puoi assumere che in tutte le istanze che utilizzeremo per validare il tuo algoritmo valga che $n \leq 100$.

In ogni caso, l'esecuzione del tuo algoritmo verrà interrotta se esso finirà per richiedere oltre un secondo effettivo di tempo di calcolo. A quel punto la tua soluzione sarà quantomeno troppo fantasiosa e non la considereremo vaida per il raggiungimento del goal (forse avremo dovuto scegliere un'altra etichetta per il nome di questo goal?).


### Ulteriori spiegazioni di valenza generale

Nel file da sottomettere, o sperimentare in locale, devi implementare la funzione `max_index`. Puoi partire dal file di template per il linguaggio di programmazione da te scelto, purchè tra quelli già supportati da TuringArena (vedi se il comando `turingarena file sync` genera il template per quel linguaggio).


Nei fatti, la sequenza `a` sarà un array in molti dei linguaggi di programmazione supportati, e tipicamente gli elementi dell'array saranno indicizzati da `0` a `n-1`. Per quasi tutti i linguaggi gli `n` elementi della sequenza saranno del tipo signed a 32 bit, che ci attendiamo rappresentati in complemento sulla totalità delle architetture, ma ovvimanete tutti questi dettagli non dovrebbero finire per riguardarti.

Chi crea il problema (il *problem-maker*, confidiamo un giorno tu stesso sarai uno dei nostri), ha solo scritto, una volta per tutte (e varrà anche per linguaggi di programmazione introdotti supportati in futuro o magari non ancora inventati), la seguente dichiarazione nel file `interface.txt`:

```function max_index(n, a[])```

e l'idea è che essa riceva in ingresso una sequenza `a`  di `n` valori scalari e ritorni uno scalare (dato che è una function piuttosto che non una procedura). Nel linguaggio di `interface.txt`, per scalari intendiamo gli interi (maggiori dettagli sul tipo specifico di interi più sotto).
Quando avrai svolto l'esercizio, ti invitiamo a dare un'occhiata al file `interface.txt` per meglio comprendere ed interagire con la struttura generale dell'ambiente che ti offriamo con TuringArena.
Le righe successive alla dichiarazione della funzione `max_index` servono per la generazione automatica dello skeleton, un file che compilato od interpretato (a seconda del linguaggio), ma comunque eseguito, insieme alla tua soluzione, ti consente di testarla in locale per essere più autonomo nella tua esperienza e percorso che ci auguriamo possa condurti lontano.

Dicevamo che per la maggior parte dei linguaggi gli scalari si mapperanno su quel tipo di interi con segno che trovano rappresentazione in 32 bits, la motivazione sottostante alla scelta è quella della più ampia portabilità e della naturallezza dell'uso nel linguaggio spefico. Ad esempio, nel caso di Python, gli interi sono quelli veri della matematica (la versione di Python presa a riferimento è Python3).
