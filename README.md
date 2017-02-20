# Thread & needles v2

Ceci est une tentative de réécriture du site [Thread & needles][tn]. Ce nouveau site est contruit
avec [Django][django].

## Statut

Presque prêt à déployer. Le site en développement est hébergé à <https://tn2.hardcoded.net>.

## Développement

Côté développement, c'est un peu compliqué de déployer sans avoir accès aux dumps de l'ancien site
WP et je n'ai pas encore fait tous les efforts pour rendre le projet *developer-friendly*. Mais si
ça vous intéresse de participer au développement, n'hésitez pas à me contacter, je vais vous aider.
Mon courriel est sur mon profil github.

Aussi, si vous n'êtes pas sous Linux, LXD-Nomad ne marchera pas. Mais dans ce cas là, on
bidouillera pour ajouter aussi une config Vagrant.

### Développement local

Le site est monté de façon à utiliser [LXD-Nomad][nomad] (comme [Vagrant][vagrant], mais pour
[LXD][lxd]) pour faire du développement local. LXD-nomad est un peu compliqué à installer, mais
une fois que c'est fait, c'est la seule dépendance. On peut ensuite déployer le site localement
en faisant:

    nomad up

Une fois le provisioning complété, on peut accéder au site local par <http://tn2.local>.
Alternativement on peut rouler le serveur de développement de Django en faisant:

    nomad shell
    ./develop.sh

Le site devient alors disponible sous <http://tn2.local:8080>.

La routine d'initialisation importe automatiquement des données "exemples" qui sont tirées de la
vraie base de donnée T&N (mais avec beaucoup, *beaucoup* moins de données). Les hash de mot de
de passe et les adresses courriel ont été anonymisées, mais pour le reste, les données sont une
copie des vraies. Ça nous permet de plus facilement travailler sur le site.

### Se créer un utilisateur admin

Pour se créer un utilisateur admin, faire:

    nomad shell
    ./manage.sh createsuperuser

[tn]: http://www.threadandneedles.fr/
[django]: https://www.djangoproject.com/
[nomad]: https://github.com/lxd-nomad/lxd-nomad
[vagrant]: https://www.vagrantup.com/
[lxd]: https://linuxcontainers.org/lxd/
