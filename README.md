# Thread & needles v2

Ceci est le code qui fait rouler [Thread & needles][tn]. Ce site est construit avec
[Django][django].

## Développement

On peut déployer le site manuellement sur son poste, mais c'est un peut plus
compliqué.  Premièrement, il faut s'assurer qu'on a toutes les dépendances:

1. Un environnement GNU avec `make`, `gcc`, etc.
1. Python 3.5+ avec support `venv`.
1. PostgreSQL 9.5+ avec une base de donnée pré-créee pour le projet.
1. [entr][entr] si on veut rouler `make watch`.

Ensuite, il faut créer un fichier de configuration. Commencez par copier `install/conf.json.example`
à la racine sous `conf.json` puis modifiez à souhait. Pour avoir une idée des possibilités de
configuration, regardez en haut du fichier `src/tn2/settings.py`.

Il suffit ensuite de rouler `make`. Une fois ça de fait, le script `manage.sh` à la racine
devrait marcher normalement. Vous pouvez donc rouler `./manage.sh load_initial_data` suivi de
`./manage.sh runserver` pour avoir un site de développement accessible à `http://localhost:8080`.

### load_initial_data

À noter que la partie `./manage.sh load_initial_data` n'est nécessaire que lorsque vous venez tout
juste de créer un environnement neuf. C'est la routine d'initialisation qui importe automatiquement
des données "exemples" qui sont tirées de la vraie base de donnée T&N (mais avec beaucoup,
*beaucoup* moins de données). Les hash de mot de de passe et les adresses courriel ont été
anonymisées, mais pour le reste, les données sont une copie des vraies. Ça nous permet de plus
facilement travailler sur le site.

### Se créer un utilisateur admin

Pour se créer un utilisateur admin, faire:

    ./manage.sh createsuperuser

Vous pourrez alors accéder à l'interface d'admin de Django en tant que super-utilisateur et faire
plein de manipulations pratiques.

### make watch

Si on travaille sur le style SCSS, ça peut être pratique d'avoir celui-ci qui se compile à chaque
changement qu'on fait. Pour ce faire, on peut utiliser la commande `make watch`.

[tn]: http://www.threadandneedles.fr/
[django]: https://www.djangoproject.com/
[entr]: http://entrproject.org/
