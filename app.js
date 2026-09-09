import { TABEL } from "./date.js";

const { temperaturi, concentratii, valori, masuratDeLa } = TABEL;
const T_MIN = temperaturi[0], T_MAX = temperaturi.at(-1);
const C_MIN = concentratii[0], C_MAX = concentratii.at(-1);

/** Poziția lui x în șirul crescător v: indicele de sub el și cât de departe e. */
function incadreaza(v, x) {
  if (x <= v[0]) return [0, 0];
  if (x >= v.at(-1)) return [v.length - 2, 1];
  let i = 0;
  while (v[i + 1] < x) i++;
  return [i, (x - v[i]) / (v[i + 1] - v[i])];
}

/** Tăria reală la 20 °C, interpolată liniar între cele patru puncte vecine. */
export function corecteaza(temp, citit) {
  const [i, ft] = incadreaza(temperaturi, temp);
  const [j, fc] = incadreaza(concentratii, citit);
  const sus = valori[i][j] + (valori[i][j + 1] - valori[i][j]) * fc;
  const jos = valori[i + 1][j] + (valori[i + 1][j + 1] - valori[i + 1][j]) * fc;
  return sus + (jos - sus) * ft;
}

/* ------------------------------------------------------------- interfața */

const el = (id) => document.getElementById(id);
const temp = el("temp"), citit = el("citit");
const tempGlisor = el("temp-glisor"), cititGlisor = el("citit-glisor");
const iesire = el("iesire"), delta = el("delta"), avert = el("avert");

/* Aplicatia scrie si citeste cu virgula, ca tastatura romaneasca. */
const nr = (x) => x.toLocaleString("ro-RO", { minimumFractionDigits: 1, maximumFractionDigits: 1 });

function citesteCamp(camp, min, max) {
  const x = parseFloat(String(camp.value).replace(",", "."));
  if (!Number.isFinite(x)) return { eroare: "gol" };
  if (x < min || x > max) return { eroare: "afara", x };
  return { x };
}

function calculeaza() {
  const t = citesteCamp(temp, T_MIN, T_MAX);
  const c = citesteCamp(citit, C_MIN, C_MAX);
  temp.classList.toggle("gresit", t.eroare === "afara");
  citit.classList.toggle("gresit", c.eroare === "afara");

  if (t.eroare || c.eroare) {
    iesire.textContent = "—";
    delta.textContent = "";
    const mesaje = [];
    if (t.eroare === "afara") mesaje.push(`temperatura trebuie să fie între ${T_MIN} și ${T_MAX} °C`);
    if (c.eroare === "afara") mesaje.push(`tăria citită trebuie să fie între ${C_MIN} și ${C_MAX} % vol`);
    arata(mesaje.length ? `Tabelul nu acoperă valoarea introdusă: ${mesaje.join("; ")}.` : "");
    return;
  }

  const real = corecteaza(t.x, c.x);
  const dif = real - c.x;
  iesire.textContent = nr(real);
  delta.textContent = Math.abs(dif) < 0.05
    ? "fără corecție la această temperatură"
    : `${dif > 0 ? "+" : "−"}${nr(Math.abs(dif))} % vol față de valoarea citită`;

  arata(t.x < masuratDeLa
    ? `Sub ${masuratDeLa} °C valoarea nu vine din tabelul tipărit, ci din prelungirea calculată a lui. Abaterea crește pe măsură ce cobori spre 0 °C.`
    : "");
  memoreaza(t.x, c.x);
}

function arata(mesaj) {
  avert.textContent = mesaj;
  avert.hidden = !mesaj;
}

/** Ține pasul între câmpul numeric și glisorul de sub el. */
function leaga(camp, glisor, min, max) {
  const potriveste = (sursa, tinta) => {
    const x = parseFloat(String(sursa.value).replace(",", "."));
    if (Number.isFinite(x) && x >= min && x <= max) tinta.value = String(x);
  };
  camp.addEventListener("input", () => { potriveste(camp, glisor); calculeaza(); });
  glisor.addEventListener("input", () => {
    camp.value = glisor.value.replace(".", ",");
    calculeaza();
  });
}

leaga(temp, tempGlisor, T_MIN, T_MAX);
leaga(citit, cititGlisor, C_MIN, C_MAX);

for (const buton of document.querySelectorAll(".pas")) {
  buton.addEventListener("click", () => {
    const camp = el(buton.dataset.tinta);
    const min = parseFloat(camp.dataset.min), max = parseFloat(camp.dataset.max);
    const acum = parseFloat(String(camp.value).replace(",", ".")) || 0;
    const nou = Math.min(max, Math.max(min, acum + parseFloat(buton.dataset.delta)));
    camp.value = String(Math.round(nou * 10) / 10).replace(".", ",");
    camp.dispatchEvent(new Event("input"));
  });
}

/* Ultimele valori introduse, ca să nu le retastezi la fiecare deschidere. */
const CHEIE = "alcoolmetru:ultimele";
function memoreaza(t, c) {
  try { localStorage.setItem(CHEIE, JSON.stringify({ t, c })); } catch { /* mod privat */ }
}
function reia() {
  try {
    const s = JSON.parse(localStorage.getItem(CHEIE) || "null");
    if (s && Number.isFinite(s.t) && Number.isFinite(s.c)) {
      temp.value = String(s.t).replace(".", ",");
      citit.value = String(s.c).replace(".", ",");
      tempGlisor.value = String(s.t);
      cititGlisor.value = String(s.c);
    }
  } catch { /* nimic memorat */ }
}

reia();
calculeaza();

/* Funcționare fără rețea. */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}
const stare = el("stare-offline");
const arataStarea = () => { stare.textContent = navigator.onLine ? "" : "Fără rețea — aplicația merge offline."; };
window.addEventListener("online", arataStarea);
window.addEventListener("offline", arataStarea);
arataStarea();
