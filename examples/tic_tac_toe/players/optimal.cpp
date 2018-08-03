#include <cstdlib>
#include <ctime>

// Constant declarations
#define ROWS 3
#define COLS 3
#define EMPTY 0
#define PLAYER 1
#define OPPONENT 2


// WARNING: I wrote these functions a lot of years ago... very ugly code
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define COMPUTER 1
#define GIOCATORE -1
#define PATTA 0

static char gioco[9];

/*
 * Funzione che ritorna true se la partita è terminata (ossia non ci sono più
 * caselle vuote) altrimenti ritorna false.
 */
int partita_finita(void) {
  int i;
  for (i = 0; i < 9; i++) {
    if (gioco[i] == ' ')
      return 0;
  }
  return 1;
}

/*
 * Funzione che ritorna il vincitore della patita:
 * GIOCATORE (-1) se la partita è vinta dal giocatore
 * COMPUTER  (1)  se la partita è vinta dal computer
 * PATTA     (0)  se la partita è finita in parità
 * 2              se la partita non è terminata
 */
int vincitore(void) {
  char risultato = 0;
  if (gioco[0]==gioco[1] && gioco[1]==gioco[2] && gioco[0]!=' ') risultato = gioco[0];
  if (gioco[3]==gioco[4] && gioco[4]==gioco[5] && gioco[3]!=' ') risultato = gioco[3];
  if (gioco[6]==gioco[7] && gioco[7]==gioco[8] && gioco[6]!=' ') risultato = gioco[6];
  if (gioco[0]==gioco[3] && gioco[3]==gioco[6] && gioco[0]!=' ') risultato = gioco[0];
  if (gioco[1]==gioco[4] && gioco[4]==gioco[7] && gioco[1]!=' ') risultato = gioco[1];
  if (gioco[2]==gioco[5] && gioco[5]==gioco[8] && gioco[2]!=' ') risultato = gioco[2];
  if (gioco[0]==gioco[4] && gioco[4]==gioco[8] && gioco[4]!=' ') risultato = gioco[4];
  if (gioco[6]==gioco[4] && gioco[4]==gioco[2] && gioco[4]!=' ') risultato = gioco[4];
  if (risultato == 'O') return GIOCATORE;
  if (risultato == 'X') return COMPUTER;
  if (partita_finita()) return PATTA;
  return 2;
}

/* 
 * Funzione che si occupa di stampare a video la matrice del gioco 
 */
// void print(void) {
//   printf(" %c | %c | %c \n", gioco[0], gioco[1], gioco[2]);
//   printf("---+---+---\n");
//   printf(" %c | %c | %c \n", gioco[3], gioco[4], gioco[5]);
//   printf("---+---+---\n");
//   printf(" %c | %c | %c \n", gioco[6], gioco[7], gioco[8]);
// }

/* 
 * Funzione che si occupa di stampare il messaggio che indica il vincitore 
 */
// void stampa_esito(int esito) {
//   if (esito == GIOCATORE) /* questo caso non potrà mai verificarsi... */
//     printf("Complimenti, hai battuto il computer!!!\n");
//   if (esito == COMPUTER)
//     printf("Ha vinto il computer\n");
//   else
//     printf("Partita finita in parità\n");
//   exit(0);
// }

/* 
 * Funzione che esegue la mossa specificata 
 */
void esegui_mossa(int mossa, int giocatore) {
  if (giocatore == GIOCATORE)
    gioco[mossa] = 'O';
  if (giocatore == COMPUTER)
    gioco[mossa] = 'X';
}

/* 
 * Funzione che fa l'undo della mossa specificata 
 */
void ripristina_mossa(int mossa) {
  gioco[mossa] = ' ';
}

/* 
 * Funzione che si occupa di controllare se la partita è terminata o meno 
 */
// void controlla_partita(void) {
//   int win;
//   print();
//   if ((win = vincitore())!=2)
//     stampa_esito(win);
// }

/* 
 * Funzione che prende l'input del giocatore 
*/
// int input_giocatore(void) {
//   int scelta;
//   do {
//     printf("Dove vuoi posizionare lo O ? (1-9) ");
//     scelta = getchar() - 49;
//     while (getchar()!='\n');
//   } while (scelta < 0 || scelta > 8 || gioco[scelta] != ' ');
//   return scelta;
// }

/*
 * Funzione ricorsiva che si occupa di calcolare una mossa e di valutarla.
 * Viene usato l'algoritmo minmax in cui si presume che il giocatore scelga la
 * mossa a lui più vantaggiosa (ossia la mossa con punteggio minimo) e il computer
 * faccia lo stesso.
 */
int testa_mossa(int mossa, int giocatore) {
  int punteggio, i, tmp;
  esegui_mossa(mossa, giocatore);
  if ((punteggio = vincitore())==2) {
    if (giocatore == COMPUTER) {
      /* minimo */
      punteggio = 10;
      for (i = 0; i < 9; i++) {
        if (gioco[i]!=' ')
          continue;
        tmp = testa_mossa(i, giocatore*-1);
        if (tmp < punteggio)
          punteggio = tmp;
      }
    } else {
      /* massimo */
      punteggio = -10;
      for (i = 0; i < 9; i++) {
        if (gioco[i]!=' ')
          continue;
        tmp = testa_mossa(i, giocatore*-1);
        if (tmp > punteggio)
          punteggio = tmp;
      }
    }
  }
  ripristina_mossa(mossa);
  return punteggio;
}


/*
 * Funzione che si occupa di calcolare la mossa del computer, eseguendo la mossa
 * che testata da un punteggio più alto
 */
int mossa_computer(void){
  int mossa = 0, i, punteggio, tmp;
  punteggio = -10;
  for (i = 0; i < 9; i++) {
    if (gioco[i]!=' ')
      continue;
    tmp = testa_mossa(i, COMPUTER);
    if (tmp > punteggio) {
      punteggio = tmp;
      mossa = i;
    }
  }
  //printf("Il computer ha scelto di muovere in %d\n", mossa+1);
  return mossa;

}

// int main(void) {
//   memset(gioco, ' ', 9);
//   print();
//   for (;;) {
//     esegui_mossa(input_giocatore(), GIOCATORE);
//     controlla_partita();
//     esegui_mossa(mossa_computer(), COMPUTER);
//     controlla_partita();
//   }
//   return 0;
// }

void play_move(int **grid, void place_at(int y, int x)) {
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            char x; 
            switch (grid[i][j]) {
            case PLAYER: x = 'X'; break;
            case OPPONENT: x = 'O'; break;
            default: x = ' ';
            }
            gioco[i * 3 + j] = x;
        }
    }

    int move = mossa_computer();

    place_at(move / 3, move % 3);
}
