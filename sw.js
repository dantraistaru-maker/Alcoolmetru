// Cache simplu: aplicatia e statica si mica, deci o tinem intreaga offline.
// Schimba VERSIUNE la fiecare actualizare, ca telefoanele sa ia fisierele noi.
const VERSIUNE = "alcoolmetru-v4";
const FISIERE = [
  "./", "./index.html", "./styles.css", "./app.js", "./date.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png", "./icons/icon-512.png",
  "./icons/icon-maskable-512.png", "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png", "./icons/favicon-64.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSIUNE).then((c) => c.addAll(FISIERE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((chei) => Promise.all(chei.filter((k) => k !== VERSIUNE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  if (new URL(e.request.url).origin !== self.location.origin) return;
  // Intai de pe retea, cu cache-ul ca plasa de siguranta. Invers - cum era
  // pana acum - o versiune noua nu ajungea pe telefon decat dupa doua
  // reincarcari, fiindca pagina veche se servea din cache inaintea ei.
  e.respondWith(
    fetch(e.request)
      .then((raspuns) => {
        if (raspuns.ok) {
          const copie = raspuns.clone();
          caches.open(VERSIUNE).then((c) => c.put(e.request, copie));
        }
        return raspuns;
      })
      .catch(() => caches.match(e.request).then((din_cache) =>
        din_cache || caches.match("./index.html")))
  );
});
