function jsonRequest(url, args) {
    return fetch(url, {
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(args),
    });
}


const AUTH_ENDPOINT = "/api/auth";


function authRequest(contest, username, password) {
    return new Promise((resolve, reject) => {
        jsonRequest(AUTH_ENDPOINT, {
            username: username,
            password: password,
            contest: contest,
        }).then(response => {
            if (response.status !== 200) {
                response.json().then(r => reject(r.message));
            } else {
                resolve();
            }
        });
    });
}


function logoutRequest(contest) {
    return authRequest(contest, null, null);
}

