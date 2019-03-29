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


const SUBMIT_ENDPOINT = "/api/evaluate";


function evaluateRequest(contest, problem, files) {
    return new Promise((resolve, reject) => {
        jsonRequest(SUBMIT_ENDPOINT, {
            contest: contest,
            problem: problem,
            files: files,
        }).then(response => {
            response.json().then(r => {
                if (response.status !== 200) {
                    reject(r.message);
                } else {
                    resolve(r);
                }
            })
        })
    });
}


function buildFileList(fileInput) {
    return new Promise(resolve => {
        let file = fileInput.files[0];
        let reader = new FileReader();

        reader.readAsText(file);
        reader.onload = () => {
            resolve({
                source: {
                    filename: file.name,
                    content: reader.result,
                }
            });
        };
    });
}
