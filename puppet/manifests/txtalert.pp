# Defaults for exec
user {"ubuntu":
    ensure => "present",
    home => "/home/ubuntu",
    shell => "/bin/bash"
}

file { "/home/ubuntu":
    ensure => "directory",
    owner => "ubuntu";
}

# Globally set exec paths and user.
Exec {
    path => ["/bin", "/usr/bin", "/usr/local/bin"],
    user => 'ubuntu',
}


# Install required packages.
class txtalert::packages {
    package { [
        "build-essential",
        "python",
        "python-dev",
        "python-setuptools",
        "python-pip",
        "python-virtualenv",
        "postgresql-8.4",
        "libpq-dev",
        "rabbitmq-server",
        "git-core",
        "openjdk-6-jre-headless",
        "libcurl4-openssl-dev",
        "memcached",
        "tidy",
        "curl",
        "nginx"]:
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
        command => "git checkout -b develop origin/develop",
        cwd => "/var/praekelt/txtalert",
        unless => "git branch | grep '* develop'",
        require => Exec['update_repo'];
    }
}

# Bugfix for https://bitbucket.org/jespern/django-piston/issue/173/
file { "/var/praekelt/txtalert/ve/lib/python2.6/site-packages/piston/__init__.py":
    ensure => "file",
    owner => "ubuntu",
}

# Create logs path.
file { "/var/praekelt/txtalert/logs":
    ensure => "directory",
    owner => "ubuntu",
}

# Create these accounts
class txtalert::accounts {
    postgres::role { "txtalert":
        ensure => present,
        password => txtalert,
    }
}

class txtalert::database {
    postgres::database { "txtalert_dev":
        ensure => present,
        owner => txtalert,
        template => "template0",
    }
}

file {
    "/var/praekelt":
        ensure => "directory",
        owner => "ubuntu";
}

file {
    "/home/ubuntu/.ssh":
        ensure => "directory",
        owner => "ubuntu",
}

file {
    "/home/ubuntu/.ssh/config":
        ensure => "file",
        owner => "ubuntu",
        content => "
Host github.com
    StrictHostKeyChecking no
"
}

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

file { "/etc/nginx/sites-enabled/development.txtalert.conf":
    ensure => symlink,
    target => "/var/praekelt/txtalert/config/nginx/development.conf"
}

exec { "Syncdb":
    command => ". ve/bin/activate && \
                    ./manage.py syncdb --noinput --settings=environments.develop && \
                deactivate
                ",
    cwd => "/var/praekelt/txtalert",
}
exec { "Migrate":
    command => ". ve/bin/activate && \
                    ./manage.py migrate --no-initial-data --settings=environments.develop && \
                deactivate
                ",
    timeout => "0",
    cwd => "/var/praekelt/txtalert",
}

exec { "Restart txtAlert":
    command => ". ve/bin/activate && \
                    supervisorctl -c supervisord.develop.conf reload && \
                deactivate",
    cwd => "/var/praekelt/txtalert",
    onlyif => "ps -p `cat tmp/pids/supervisord.pid`"
}
exec { "Start txtAlert":
    command => ". ve/bin/activate && \
                    supervisord -c supervisord.develop.conf && \
                deactivate",
    cwd => "/var/praekelt/txtalert",
    unless => "ps -p `cat tmp/pids/supervisord.pid`"
}

exec { "Collect static":
    command => ". ve/bin/activate && \
                    ./manage.py collectstatic --settings=environments.develop --noinput && \
                deactivate",
    cwd => "/var/praekelt/txtalert"
}

class txtalert {
    #include apt::update,
    include 
        txtalert::accounts, 
        txtalert::packages, 
        txtalert::database,
        txtalert::repo,
        txtalert::ve
}

User["ubuntu"]
    -> File["/home/ubuntu"]
    -> File["/var/praekelt"] 
    -> File["/home/ubuntu/.ssh"] 
    -> File["/home/ubuntu/.ssh/config"] 
    -> Class["txtalert::packages"] 
    -> Class["txtalert::accounts"]
    -> Class["txtalert::database"]
    #-> File["/etc/nginx/sites-enabled/development.txtalert.conf"]
    -> Class["txtalert::repo"]
    -> File["/var/praekelt/txtalert/logs"]
    -> Class["txtalert::ve"]
    #-> Exec["Create virtualenv"] 
    #-> Exec["Install requirements"] 
    -> File["/var/praekelt/txtalert/ve/lib/python2.6/site-packages/piston/__init__.py"]
    -> Exec['Syncdb']
    -> Exec['Migrate']
    -> Exec['Collect static']
    -> Exec["Restart txtAlert"]
    -> Exec["Start txtAlert"]

include txtalert
