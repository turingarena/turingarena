# Triangolo

preso da Gara IOI 1994


## Descrizione del problema

```
     7
    3 8
   8 1 0
  2 7 4 4
 4 5 2 6 6
```

Questo è un triangolo di $N = 5$ righe.



Siamo interessati in quei cammini che partono dal vertice in alto (dove nell'esempio si trova un 7) e discendono prendendo un elemento da ciascuna riga, fino all'ultima. Ogni cammino prende pertanto $5$ elementi.
Il valore di un cammino è la somma degli elementi presi.
Vogliamo trovare il massimo valore di un cammino.
Un possibile cammino potrebbe essere ad esempio quello che raccogli i seguenti valori: 7 3 1 7 5. Il suo valore è $7+3+1+7+5 = 23$ mentre il massimo valore di un cammino, in questo caso, dovrebbe essere $30$.

Le righe del triangolo sono numerate partendo da $1$ ed ogni elemento del triangolo risulta univocamente determinat da una coppia $(r,c)$ dove $r$ indica l'indice della riga che lo contiene mentre $c\geq 0$ specifica che si tratta del $c$-esimo elemento della riga $r$.
In pratica gli elementi del triangolo sono numerati come segue:

```
                 (1,0)
              (2,0) (2,1)
           (3,0) (3,1) (3,2)
        (4,0) (4,1) (4,2) (4,3)
     (5,0) (5,1) (5,2) (5,3) (5,4)
```

Se un camino valido prende un elemento $(r,c)$ con $r < N$ allora nella riga successiva prende o l'elemento $(r+1,c)$ oppure l'elemento $(r+1,c+1)$.

Devi scrivere la funzione `find_best_sum(N,V)` che prende in input un triangolo caratterizzato dal numero di righe `N` e come tabella di valori `V` tale che `V[r][c]` sia il valore dell'elemento del triangolo che abbiamo numerato dall coppia $(r,c)$.
La funzione deve restituire il massimo valore di un cammino.

## Assunzioni

* $1 < N \le 100$.

## Goals:

1. correct
2. i valori del triangolo sono tutti uguali.
3. $N = 10$.
4. $N = 30$.
5. $N = 100$.

