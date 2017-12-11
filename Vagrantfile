Vagrant.configure("2") do |config|
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = false

  config.vm.box = "debian/stretch64"

  config.vm.define "web", primary: true do |web|
    web.vm.hostname = "tn2"
    web.hostmanager.aliases = %w(tn2.local)

    web.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "ansible/site.yml"
      ansible.become = true
    end
  end

  config.vm.define "debbuild", autostart: false do |build|
    build.hostmanager.enabled = false
    build.vm.provision "ansible_local" do |ansible|
      ansible.playbook = "ansible/debbuild.yml"
      ansible.become = true
    end
  end
end
