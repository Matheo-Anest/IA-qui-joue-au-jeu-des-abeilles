# 🐝 IA qui joue au Jeu des Abeilles

Ce projet permet de simuler et d'observer des affrontements entre différentes Intelligences Artificielles au sein du jeu des abeilles.

## 🚀 Lancement du projet

1. Ouvrez un terminal dans le dossier du projet.
2. Lancez le script principal :
   ```bash
   python jouer.py

## 🎮 Mode d'emploi
### Étape 1 : Configuration
Au lancement de jouer.py, une fenêtre s'ouvre pour configurer la partie :

- **Choix des IA :** Sélectionnez l'algorithme souhaité pour chaque joueur.

- **Validation :** Cliquez sur le bouton pour générer et lancer la partie.

### Étape 2 : Visualisation
Une fois la partie lancée, une nouvelle fenêtre affiche le plateau :

- **Observation :** Suivez les mouvements et les décisions des IA en temps réel.

- **Accélération :** Vous pouvez augmenter la vitesse de simulation jusqu'en x16 pour voir rapidement l'issue du match.

## 📂 Structure du dépôt
- **jouer.py :** Point d'entrée principal (configuration et lancement).

- **rejouer.py :** Permet de visionner une partie enregistrée.

- **ia/ :** Répertoire contenant les différents algorithmes d'IA.

- **bzzz/ :** Logique interne et moteur du jeu.

- **assets/ :** Ressources graphiques et images du jeu.

<br>
<br>

#### **Documentation de la stratégie de mon IA :**

**1. Philosophie Globale :**

Mon IA s'adapte à la situation. Au lieu de garder toujours le même plan, j'ai fait en sorte qu'elle observe le jeu en direct (nombre de joueurs, fleurs disponibles) et change sa façon de jouer. L'objectif est simple : rendre les ouvrières super efficaces et utiliser les bourdons pour embêter précisément les adversaires.

**2. Gestion de la ponte :**

Mon système de reproduction ne suit pas un schéma fixe, mais s'adapte à deux facteurs critiques que j'ai identifiés :

- **La densité de ressources :** Le nombre d'ouvrières et de bourdons évolue selon le nombre de fleurs sur le plateau (plus de 12, 8, ou moins). En effet, s'il n'y en a pas beaucoup, mon IA réduit la production pour économiser le nectar.
- **Le nombre d'adversaires :** - En 1v1 : J'adopte une stratégie agressive avec plus de bourdons.
    - À 4 joueurs : Je passe sur une stratégie prudente, focalisée sur la récolte, en attaquant les deux ennemis à mes côtés avec un seul bourdon chacun.

**3. Stratégie des ouvrières :**

- **A. Travail d'équipe :** Si une abeille vise une fleur, les autres le savent et choisissent une autre cible. Comme ça, personne ne fait le trajet pour rien.
- **B. Zone de confiance :** J'ai défini une zone autour de ma base :
    - Dans cette zone, mon abeille ne rentre pas à la base tant qu'elle n'est pas à son stock maximum.
    - En dehors de cette zone, dès qu'elle a au moins 5 de nectar, elle rentre sécuriser le butin pour éviter les risques.
- **C. Mémoire et sécurité :** Mes abeilles se souviennent des fleurs vides pour ne pas y retourner. Et si une fleur se vide pile au moment où elles récoltent, elles rentrent directement à la base avec ce qu'elles ont.

**4. Stratégie des bourdons :**

Mes bourdons ont pour rôle de faire perdre le nectar des ouvrières adverses.

- **Ciblage :** Dans les parties à 4 joueurs, mes bourdons ne visent que les deux adversaires à côté de moi et pas celui en diagonale qui est trop loin (traverser le terrain serait une perte de temps).
- **Traque :** Chaque bourdon est assigné à un joueur cible et cherche en priorité à mettre KO ses ouvrières actives. Cependant, s'il croise d'autres abeilles ennemies sur sa route, il les mettra également KO.
- **Sécurité :** Si aucune cible n'est valide, le bourdon se dirige vers la base de l'ennemi auquel il est assigné. Cela évite qu'un bourdon sans cible ne bloque la ruche, me permettant de continuer à faire apparaître d'autres unités.

**5. Déplacements :**

Mon moteur de déplacement utilise un algorithme avec évitement d'obstacles :

- **Priorité à l'axe le plus long** pour réduire la distance rapidement.
- **Détection des déplacements interdits** avec les alliés, les ennemis, les bases adverses et les sorties de terrain.
- **Contournement automatique :** Si le chemin direct est bloqué, l'IA tente automatiquement un contournement par l'autre axe.
