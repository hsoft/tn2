# Thread & needles v2

Ceci est le code qui fait rouler [Thread & needles][tn]. Ce site est construit avec
[Django][django].

## Développement

Pour développer le site sur son poste local, il y deux options.

### Option 1: LXDock

Le site est monté de façon à utiliser [LXDock][lxdock] (comme [Vagrant][vagrant], mais pour
[LXD][lxd]) pour faire du développement local. LXDock est un peu compliqué à installer, mais
une fois que c'est fait, c'est la seule dépendance. On peut ensuite déployer le site localement
en faisant:

    git submodule init
    git submodule update
    lxdock up

Une fois le provisioning complété, on peut accéder au site local par <http://tn2.local>.
Alternativement on peut rouler le serveur de développement de Django en faisant:

    lxdock shell
    ./manage.sh load_initial_data
    ./develop.sh

Le site devient alors disponible sous <http://tn2.local:8080>.


### Option 2: Déploiement manuel

On peut aussi déployer le site manuellement sur son poste, mais c'est un peut plus compliqué.
Premièrement, il faut s'assurer qu'on a toutes les dépendances:

1. Un environnement GNU avec `make`, `gcc`, etc.
1. Python 3.4+ avec support `venv`.
1. PostgreSQL 9.5+ avec une base de donnée pré-créee pour le projet.

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

    lxdock shell
    ./manage.sh createsuperuser

Vous pourrez alors accéder à l'interface d'admin de Django en tant que super-utilisateur et faire
plein de manipulations pratiques.

[tn]: http://www.threadandneedles.fr/
[django]: https://www.djangoproject.com/
[lxdock]: https://github.com/lxdock/lxdock
[vagrant]: https://www.vagrantup.com/
[lxd]: https://linuxcontainers.org/lxd/
