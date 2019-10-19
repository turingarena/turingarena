use crate::{token, ENDPOINT};

/// make a request to the server
pub fn request<T, R>(body: &T) -> R
where
    T: serde::Serialize + ?Sized,
    R: serde::de::DeserializeOwned,
{
    reqwest::Client::new()
        .post(unsafe { &ENDPOINT })
        .json(&body)
        .send()
        .expect("Error in network request")
        .json()
        .expect("Error getting the response")
}

/// make a request to the server, providing the authorization token
pub fn authenticated_request<T, R>(body: &T) -> R
where
    T: serde::Serialize + ?Sized,
    R: serde::de::DeserializeOwned,
{
    let token = token::get().expect("You need to login first");
    reqwest::Client::new()
        .post(unsafe { &ENDPOINT })
        .header("Authorization", token)
        .json(&body)
        .send()
        .expect("Error in network request")
        .json()
        .expect("Error getting the response")
}
