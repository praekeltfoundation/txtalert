# Globally set exec paths and user.
Exec {
    path => ["/bin", "/usr/bin", "/usr/local/bin"],
    user => 'ubuntu',
}

# System setup/init class.
class txtalert::sysinit {
    # Create required paths and files.
    file { "ubuntu_home":
        path => "/home/ubuntu",
        ensure => "directory",
        owner => "ubuntu";
    }

    file { "webapp_path":
        path => "/var/praekelt",
        ensure => "directory",
        owner => "ubuntu";
    }

    file { "ubuntu_ssh_path":
        path => "/home/ubuntu/.ssh",
        ensure => "directory",
        owner => "ubuntu",
    }

    file { "ubuntu_ssh_config":
        path => "/home/ubuntu/.ssh/config",
        ensure => "file",
        owner => "ubuntu",
        content => "
Host github.com
    StrictHostKeyChecking no
    "
    }

    # Adds a line to a file if not already present.
    define line($file, $line) {
        exec { "echo '${line}' >> ${file}":
            user => "root",
            unless => "grep '${line}' ${file}"
        }
    }
    
    # Stop HAProxy complaining about file limits.
    line {"soft_limit":
        file => "/etc/security/limits.conf",
        line => "ubuntu soft nofile 16384"
    }

    line {"hard_limit":
        file => "/etc/security/limits.conf",
        line => "ubuntu hard nofile 16384"
    }
    
    line {"pam_limits":
        file => "/etc/pam.d/common-session",
        line => "session required pam_limits.so"
    }
    
    # Install required packages.
    package { [
        "build-essential",
        "curl",
        "git-core",
        "haproxy",
        "libcurl4-openssl-dev",
        "libpq-dev",
        "memcached",
        "nginx",
        "openjdk-6-jre-headless",
        "python",
        "python-dev",
        "python-setuptools",
        "python-pip",
        "python-virtualenv",
        "postgresql-8.4",
        "rabbitmq-server",
        "supervisor",
        "tidy"]:
        ensure => latest, 
        require => Exec['update_apt'];
    }

    # Update package index.
    exec { "update_apt":
        command => "apt-get update",
        user => "root",
    }
}

# Clone, update and checkout development repo.
class txtalert::repo {
    exec { "clone_repo":
        command => "git clone https://github.com/smn/txtalert.git",
        cwd => "/var/praekelt",
        unless => "test -d /var/praekelt/txtalert/.git"
    }

    exec { "update_repo":
        command => "git pull",
        cwd => "/var/praekelt/txtalert",
        onlyif => "test -d /var/praekelt/txtalert/.git",
        require => Exec['clone_repo'];
    }
    
    exec { "checkout_dev_branch":
        #command => "git checkout -b develop origin/develop",
        command => "git checkout -b feature/envcleanup origin/feature/envcleanup",
        cwd => "/var/praekelt/txtalert",
        #unless => "git branch | grep '* develop'",
        unless => "git branch | grep '* feature/envcleanup'",
        require => Exec['update_repo'];
    }

    # Create logs path.
    file { "/var/praekelt/txtalert/logs":
        ensure => "directory",
        owner => "ubuntu",
    }
}

# Bugfix class.
class txtalert::bugfixes {
    # Bugfix for https://bitbucket.org/jespern/django-piston/issue/173/
    file { "piston_bugfix_173":
        path => "/var/praekelt/txtalert/ve/lib/python2.6/site-packages/piston/__init__.py",
        ensure => "file",
        owner => "ubuntu",
    }
}

# Configure database.
class txtalert::database {
    postgres::role { "txtalert":
        ensure => present,
        password => txtalert,
    }
    
    postgres::database { "txtalert_dev":
        ensure => present,
        owner => txtalert,
        template => "template0",
    }
}

# Create and init ve.
class txtalert::ve {
    exec { "create_virtualenv":
        command => "virtualenv --no-site-packages ve",
        cwd => "/var/praekelt/txtalert",
        unless => "test -d ve"
    }

    exec { "pip_requirements":
        command => ". ve/bin/activate && \
                        pip install -r requirements.pip && \
                    deactivate",
        cwd => "/var/praekelt/txtalert",
        timeout => "0", # disable timeout
        onlyif => "test -d ve",
        require => Exec['create_virtualenv'];
    }
}

class txtalert::symlinks {
    file { "/etc/nginx/sites-enabled/development.txtalert.conf":
        ensure => symlink,
        target => "/var/praekelt/txtalert/config/nginx/development.conf"
    }
    
    file { "/etc/nginx/sites-enabled/default":
        ensure => absent,
    }

    file { "/etc/supervisor/conf.d/supervisord.develop.conf":
        ensure => symlink,
        target => "/var/praekelt/txtalert/supervisord.develop.conf"
    }
}

class txtalert::django_maint {
    exec { "django_syncdb":
        command => ". ve/bin/activate && \
                    ./manage.py syncdb --noinput --settings=environments.develop && \
                    deactivate",
        cwd => "/var/praekelt/txtalert",
    }

    exec { "django_migrate":
        command => ". ve/bin/activate && \
                    ./manage.py migrate --no-initial-data --settings=environments.develop && \
                    deactivate",
        timeout => "0",
        cwd => "/var/praekelt/txtalert",
    }

    exec { "django_collect_static":
        command => ". ve/bin/activate && \
                    ./manage.py collectstatic --settings=environments.develop --noinput && \
                    deactivate",
        cwd => "/var/praekelt/txtalert"
    }
}

# Reload supervisor thus (re)starting processes.
exec { "supervisor_reload":
    command => "supervisorctl reload",
    user => "root",
}

class txtalert {
    include 
        txtalert::bugfixes,
        txtalert::database, 
        txtalert::django_maint, 
        txtalert::repo,
        txtalert::symlinks,
        txtalert::sysinit,
        txtalert::ve
}

# Create 'ubuntu' user.
user { "ubuntu":
    ensure => "present",
    home => "/home/ubuntu",
    shell => "/bin/bash"
}

User["ubuntu"]
    -> Class["txtalert::sysinit"] 
    -> Class["txtalert::database"] 
    -> Class["txtalert::repo"] 
    -> Class["txtalert::ve"] 
    -> Class["txtalert::bugfixes"] 
    -> Class["txtalert::django_maint"] 
    -> Class["txtalert::symlinks"] 
    -> Exec["supervisor_reload"]
    
include txtalert
