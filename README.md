# Thread & needles v2

Ceci est une tentative de réécriture du site [Thread & needles][tn]. Ce nouveau site est contruit
avec [Django][django].

## Statut

Très préliminaire. Le site en développement est hébergé à <https://tn2.hardcoded.net>.

## Développement local

Le site est monté de façon à utiliser [LXD-Nomad][nomad] (comme [Vagrant][vagrant], mais pour
[LXD][lxd]) pour faire du développement local. LXD-nomad est un peu compliqué à installer, mais
une fois que c'est fait, c'est la seule dépendance. On peut ensuite déployer le site localement
en faisant:

    nomad up

Une fois le provisioning complété, on peut accéder au site local par <http://tn2.local>.
Alternativement on peut rouler le serveur de développement de Django en faisant:

    lxc exec tn2 bash
    su tn2
    cd /opt/tn2
    . env/bin/activate
    cd project/src
    python manage.py runserver 0.0.0.0:8080

Le site devient alors disponible sous <http://tn2.local:8080>.

[tn]: http://www.threadandneedles.fr/
[django]: https://www.djangoproject.com/
[nomad]: https://github.com/lxd-nomad/lxd-nomad
[vagrant]: https://www.vagrantup.com/
[lxd]: https://linuxcontainers.org/lxd/
