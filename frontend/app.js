const formEl = document.getElementById("form-mode");
const jsonFormEl = document.getElementById("json-mode");
const jsonInputEl = document.getElementById("json-input");
const jsonParseErrorEl = document.getElementById("json-parse-error");
const outputEl = document.getElementById("output");
const errorOutputEl = document.getElementById("error-output");

function clearMessages() {
  jsonParseErrorEl.textContent = "";
  errorOutputEl.textContent = "";
}

async function callApi(payload) {
  clearMessages();
  outputEl.textContent = "Enviando requisição para /plan-activity...";

  try {
    const response = await fetch("/plan-activity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    let text;
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
      text = JSON.stringify(await response.json(), null, 2);
    } else {
      text = await response.text();
    }

    if (!response.ok) {
      errorOutputEl.textContent =
        "Erro da API (status " + response.status + "). Veja o detalhe abaixo.";
    }

    outputEl.textContent = text;
  } catch (err) {
    errorOutputEl.textContent = "Erro de rede: " + err.message;
    outputEl.textContent = "";
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();

  const latitude = parseFloat(document.getElementById("latitude").value);
  const longitude = parseFloat(document.getElementById("longitude").value);
  const date = document.getElementById("date").value;

  const payload = { latitude, longitude, date };
  await callApi(payload);
});

jsonFormEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessages();

  const raw = jsonInputEl.value.trim();
  if (!raw) {
    jsonParseErrorEl.textContent = "Cole um JSON válido antes de enviar.";
    return;
  }

  try {
    const payload = JSON.parse(raw);
    await callApi(payload);
  } catch (err) {
    jsonParseErrorEl.textContent = "Erro ao interpretar JSON: " + err.message;
  }
});