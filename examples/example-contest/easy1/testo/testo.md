# Trova il massimo

Topolino ha ricevuto in regalo una sequenza di $N$ numeri interi. Puoi aiutarlo
a trovare il numero più grande presente nella sequenza scrivendo un programma?
Se $N$ fosse uguale a 12 e la sequenza ricevuta da Topolino fosse la seguente:

|||||||||||||
|-|-|-|-|-|-|-|-|-|-|-|-|
-331 | -341 | 389 | 349 | -37 | -287 | 441 | -871 | -913 | -853 | -617 | -150

allora il tuo programma dovrebbe restituire $441$.

### Dati di input

Nel file **input.txt** sono presenti due righe di testo: nella prima c'è un singolo
numero intero positivo $N$; nella seconda riga ci sono gli $N$ interi $S_i$ che
compongono la sequenza di Topolino, separati da spazio.

### Dati di output

Nel file **output.txt** dovrai stampare un singolo numero intero, il valore massimo
della sequenza.

### Assunzioni
- $1 \le N \le 1000$.
- $|S_i| < 1000$, ovvero $-1000 < S_i < 1000$.

### Esempi
Input
```
12
-331 -341 389 349 -37 -287 441 -871 -913 -853 -617 -150
```

Output
```
441
```

Input
```
3
896 -242 -311
```

Output
```
896
```

Input
```
1
-677
```

Output
```
-677
```
