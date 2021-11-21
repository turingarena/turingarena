# Autorizzazione

TuringArena implementa un servizio di autorizzazione che serve le chiamate API GraphQL soltanto se l'utente che ne fa richiesta possiede i permessi necessari.

## Come abilitare o disattivare l'autorizzazione delle chiamate

Usando l'opzione `--admin` o lanciando `npm run serve-admin` o ``npm run watch:serve-admin` saranno consentite API privilegiate e non sarà controllato alcun token.
NB: usare sempre un proxy dotato di autenticazione o una rete protetta quando si usa questa modalità in produzione.

## Come effettuare chiamate all'interfaccia GraphQL quando l'autorizzazione è attiva

Per prima cosa è necessario accedere all'interfaccia online di GraphQl recandosi al link specificato all'interno del file  [`server\turingarena.config.json`](../server/turingarena.config.json) .

Nel nostro caso l'url da digitare è [`http://localhost:3000/graphql`](http://localhost:3000/graphql)

Si aprirà una pagina simile a questa:

<img src="./img/graphql_interface.png" style="zoom:80%;" />

Nella parte di sinistra andremo a inserire le nostre richieste mentre nella parte di destra il server ci mostrerà la risposta alla nostra query.

Quando l'utente si autentica dal browser viene inviata una mutazione al server Apollo nella quale viene passata la password dell'utente e in cambio il server risponde con un token. Tale token viene poi utilizzato come metodo di autenticazione per le chiamate successive.

Per richiedere il nostro token andiamo dunque a digitare il seguente codice

```
mutation{
	logIn(token: "<pwduser>"){
    	token
  	}
}
```

dove al posto di `<pwduser>` va inserita la propria password

Si vedrà apparire sulla destra una risposta simile a questa:

```
{
  "data": {
    "logIn": {
      "token": "eyJhbzZXIxIiwiaWF0IjoxNjAyGciOi
      ...
      uT1yfdCOpi_gB8NFn3Go4aFI"
    }
  }
}
```



Ora che il server ci ha comunicato il nostro token possiamo in basso a sinistra aprire la finestra HTTP HEADERS e inserire il seguente codice dove al posto di `<token>` andrà inserito il token copiato.

```
{"authorization":"Bearer <token>"}
```

Prestare attenzione a lasciare uno spazio tra `Bearer` e il token

**Esempio:**

Nella seguente schermata abbiamo un utente ( `user1` ) che ha già effettuato il login e ottenuto il proprio token che effettua due chiamate al server GraphQL . Nella chiamata di sinistra lo vediamo richiedere informazioni riguardanti a se stesso e il server gli risponde correttamente con le informazioni richieste. Quando però tenta di ottenere informazioni riguardanti un `user2` gli viene risposto che non ha i permessi per fare tale richiesta. 

![](./img/graphql_auth_query.png)

## L'autorizzazione nel codice

All'interno di [`server/src/main/api-context.ts`](../server/src/main/api-context.ts) sono presenti le funzioni `authorizeUser` e `authorizeAdmin` che vengono utilizzate all'interno del server per consentire o meno un data richiesta GraphQL.
Se l'utente ha le autorizzazioni necessarie per effettuare l'operazione le funzioni terminano correttamente, in caso contrario viene lanciato un errore.

### authorizeUser
La funzione prende come parametro una stringa che nel corretto utilizzo dovrebbe rappresentare il proprietario dell'informazione alla quale si sta tentando di accedere. 
Inizialmente viene effettuato un controllo per vedere se il parametro admin è impostato a `true` e in tal caso la funzione termina.
Se invece `admin` è false allora viene controllato se l'utente che ha fatto la richiesta è l'`username` passato come parametro oppure un admin. Se nessuna delle due condizioni viene soddisfatta viene lanciato un errore.
``` javascript
async authorizeUser(username: string) {
        if (this.environment.admin) return;

        if (this.user?.username === username) return;
        if (await this.isAdmin()) return;

        throw new Error(`Not logged in as '${username}', nor admin`);
    }
```

### authorizeAdmin
Anche in questo caso come nel precedente viene fatto un controllo iniziale per verificare se l'autorizzazione non è richiesta dalle impostazioni del server.
In caso negativo viene controllato se l'utente è loggato nel sistema come amministratore e se così non fosse viene lanciato un errore
``` javascript
async authorizeAdmin() {
        if (this.environment.admin) return;
        if (await this.isAdmin()) return;

        throw new Error(`Not authorized`);
    }
```

### Esempio d'uso delle funzioni per l'autorizzazione

All'interno del file [`server/src/core/query.ts`](../server/src/core/query.ts)) è possibile trovare il seguente uso della funzione  `authorizeUser`. 

``` javascript
export const queryResolvers: Resolvers = {
    Query: {
        //[...],
        submission: async ({}, { id }, ctx) => {
            const sub = await ctx.api(SubmissionApi).validate({ __typename: 'Submission', id });

            const username = await (await ctx.api(SubmissionApi).getUndertaking(sub)).user.username;
            await ctx.authorizeUser(username);
            return sub;
        },
        //[...],
    },
};
```

E' il codice che espone la query per ottenere una `submission`. Una `submission` rappresenta la sottomissione di una soluzione da parte di un utente ad un dato problema.

Dopo aver recuperato la sottomissione corrispondente all'`id` richiesto viene estrapolato tramite la funzione `getUndertaking` l'utente che ha effettuato la sottomissione. 
Viene quindi chiamata la funzione `authorizeUser` passando come parametro l'owner della submission. Si ottiene quindi che un user che non sia admin non può richiedere al server le sottomissioni effettuate dagli altri utenti ma solamente le proprie.

### Autorizzazioni necessarie per le varie query

#### Query


| Query | Requisito |
|-|-|
|mainView  | Se viene specificato l'user di cui si deve ottenere la vista principale <br/>allora l'utente deve essere loggato come quel specifico user o essere amministratore |
|contests |E' necessario godere dei privilegi di amministratore|
|fileContent| Query non ancora implementata   
|archive | E' necessario godere dei privilegi di amministratore    
|submission | L'utente deve essere loggato con lo stesso account dell'user di cui si sta richiedendo <br/> la sottomissione o essere amministratore |
|message |  E' necessario godere dei privilegi di amministratore |
|messages | L'utente deve essere loggato con lo stesso user di cui si stanno richiedendo i messaggi <br/> o essere amministratore  |


#### Mutation
| Mutation | Requisito |
|-|-|
| init | Non sono richiesti requisiti particolari |
| submit | L'utente deve essere loggato con lo stesso account dell'user che sta effettuando la sottomissione <br/>o essere amministratore |
| logIn | Non sono richiesti requisiti particolari |
| sendMessage | L'utente deve essere loggato con lo stesso user che sta mandando il messaggio  <br/> o essere amministratore |
