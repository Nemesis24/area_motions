# Area Motions

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

## Description

L'intégration **Area Motions** permet de gérer les détecteurs de mouvement par zone dans Home Assistant. Vous pouvez exclure certains détecteurs de chaque zone et surveiller l'état des détecteurs dans chaque zone.

## Installation

### Via HACS (Home Assistant Community Store)

1. Ajoutez ce dépôt à HACS en tant que dépôt personnalisé.
2. Recherchez "Area Motions" dans HACS et installez l'intégration.
3. Redémarrez Home Assistant.

### Manuel

1. Téléchargez les fichiers de ce dépôt.
2. Copiez le dossier `area_motions` dans le répertoire `custom_components` de votre configuration Home Assistant.
3. Redémarrez Home Assistant.

## Configuration

### Via l'interface utilisateur

1. Allez dans `Configuration` > `Intégrations`.
2. Cliquez sur le bouton `+ Ajouter une intégration`.
3. Recherchez "Area Motions" et suivez les instructions à l'écran pour configurer l'intégration.

### Via YAML

Non supporté.

## Utilisation

### Capteurs

L'intégration crée des capteurs pour chaque zone et un pour toute la maison avec les attributs suivants :

- `count`: Nombre de détecteurs de mouvement actifs.
- `total`: Nombre total de détecteurs de mouvement.
- `count_of`: Nombre de détecteurs de mouvement actifs sur le total.
- `motions_active`: Liste des détecteurs de mouvement actifs.
- `motions_inactive`: Liste des détecteurs de mouvement inactifs.
- `excluded_motions`: Liste des détecteurs de mouvement exclus.

### Exclusion de détecteurs

Vous pouvez exclure des détecteurs spécifiques de chaque zone via l'interface de configuration de l'intégration.

## Support

Pour toute question ou problème, veuillez utiliser le [suivi des problèmes](https://github.com/Nemesis24/area_motions/issues).

## Contribuer

Les contributions sont les bienvenues ! Veuillez lire le fichier [CONTRIBUTING.md](https://github.com/Nemesis24/area_motions/blob/main/CONTRIBUTING.md) pour plus d'informations.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](https://github.com/Nemesis24/area_motions/blob/main/LICENSE) pour plus de détails.