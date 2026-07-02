# TrainLog — PWA Installation

## Installation sur Android (Chrome)

1. **Télécharge les fichiers** : Place tous les fichiers dans un dossier sur un serveur web.
   - Si tu n'as pas de serveur : utilise **GitHub Pages** (gratuit) ou **Netlify** (gratuit).

2. **Option la plus simple — GitHub Pages** :
   - Crée un compte sur github.com
   - Nouveau repository public → upload tous les fichiers
   - Paramètres → Pages → Source: main branch
   - Tu obtiens une URL type : `https://tonnom.github.io/trainlog/`

3. **Sur ton téléphone Android** :
   - Ouvre l'URL dans Chrome
   - Menu ⋮ → "Ajouter à l'écran d'accueil"
   - L'app s'installe comme une vraie appli avec icône !

4. **Fonctionne hors-ligne** : une fois chargée, l'app marche sans connexion.

## Contenu du dossier
- `index.html` — Application principale
- `manifest.json` — Métadonnées PWA
- `sw.js` — Service Worker (mode hors-ligne)
- `icon-192.png` — Icône app
- `icon-512.png` — Icône splash screen

## Fonctionnalités
- ⭐ Favoris avec heure départ/arrivée théoriques + gares
- 🚀 Bouton départ → enregistre l'heure réelle
- 🏁 Bouton arrivée → calcule le retard
- 📋 Journal avec filtres (à l'heure / retard / incomplet)
- 📊 Statistiques : retard moyen, pire retard, % à l'heure, graphique
- ⬇ Export CSV
- 💾 Données stockées localement sur le téléphone
