Vagrant.configure("2") do |config|
  config.hostmanager.enabled = true
  config.hostmanager.manage_host = true
  config.hostmanager.manage_guest = false

  config.vm.box = "debian/stretch64"

  config.vm.provider :lxc do |provider|
    provider.tmpfs_mount_size = false
    provider.privileged = false
  end

  config.vm.define "web", primary: true do |web|
    web.vm.hostname = "tn2"
    web.hostmanager.aliases = %w(tn2.local)

    web.vm.provision "ansible" do |ansible|
      ansible.playbook = "ansible/site.yml"
      ansible.become = true
    end
  end
end
