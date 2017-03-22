# Thread & needles v2

Ceci est le code qui fait rouler [Thread & needles][tn]. Ce site est construit avec
[Django][django].

## Développement

Côté développement, c'est un peu compliqué de déployer sans avoir accès aux dumps du site (qui bien
sûr ne peuvent pas être partagés à tout le monde) et je n'ai pas encore fait tous les efforts pour
rendre le projet *developer-friendly*. Mais si ça vous intéresse de participer au développement,
n'hésitez pas à me contacter, je vais vous aider. Mon courriel est sur mon profil github.

Aussi, si vous n'êtes pas sous Linux, LXDock ne marchera pas. Mais dans ce cas là, on bidouillera
pour ajouter aussi une config Vagrant.

### Développement local

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
