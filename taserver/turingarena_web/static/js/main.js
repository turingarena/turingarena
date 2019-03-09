function jsonRequest(url, args) {
    return fetch(url, {
        method: 'post',
        headers: {
           'Content-Type': 'application/json',
        },
        body: JSON.stringify(args),
    });
}
