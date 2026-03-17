const BASE = "http://localhost:8000";

async function request(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) {
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(`${BASE}${path}`, opts);
  const data = await res.json();
  if (!res.ok) {
    // Throw a consistent shape matching the backend's { code, message } error payload.
    throw { status: res.status, code: data.code ?? "UNKNOWN", message: data.message ?? "Unknown error" };
  }
  return data;
}

export const createGame = (wordLength) =>
  request("POST", "/games", { word_length: wordLength });

export const getGame = (gameId) =>
  request("GET", `/games/${gameId}`);

export const submitGuess = (gameId, guess) =>
  request("POST", `/games/${gameId}/guesses`, { guess });
