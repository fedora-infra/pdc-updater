# -*- mode: ruby -*-
# vi: set ft=ruby :

$script = <<SCRIPT
    dnf install -y \
        python \
        python-devel \
        libffi-devel \
        redhat-rpm-config \
        openssl-devel \
        gcc \
        gcc-c++ \
        zeromq-devel \
        koji \
        swig \
        fedmsg \
        libyaml-devel
    cd /opt/pdc-updater/src
    python setup.py develop
    pip install -r test-requirements.txt
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "fedora/24-cloud-base"
  config.vm.provider :virtualbox do |v|
    v.customize ["modifyvm", :id, "--memory", 2048]
  end
  config.vm.synced_folder "./", "/opt/pdc-updater/src"
  config.vm.provision "shell", inline: $script
end
