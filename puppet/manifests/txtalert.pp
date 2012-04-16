# Globally set exec paths and user.
Exec {
    path => ["/bin", "/usr/bin", "/usr/local/bin"],
    user => 'ubuntu',
}

# Update package index.
exec { "update_apt":
    command => "apt-get update",
    user => "root",
}

# Ensure Ubuntu user exists
user { "ubuntu":
    ensure => "present",
    home => "/home/ubuntu",
    shell => "/bin/bash"
}

# Create the deployment directory
file { "/var/praekelt/":
    ensure => "directory",
    owner => "ubuntu",
    subscribe => User["ubuntu"]
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
    "python",
    "python-dev",
    "python-setuptools",
    "python-pip",
    "python-virtualenv",
    "postgresql",
    "supervisor"
    ]:
    ensure => latest,
    subscribe => Exec['update_apt'];
}

exec { "clone_repo":
    command => "git clone https://github.com/smn/txtalert.git",
    cwd => "/var/praekelt",
    unless => "test -d /var/praekelt/txtalert",
    subscribe => [
        Package['git-core'],
        File['/var/praekelt/'],
    ]
}

# Create logs path.
file { "/var/praekelt/txtalert/logs":
    ensure => "directory",
    owner => "ubuntu",
    subscribe => Exec['clone_repo'],
}

# Create tmp paths
file { "/var/praekelt/txtalert/tmp/":
    ensure => "directory",
    owner => "ubuntu",
    subscribe => Exec['clone_repo'],
}

# Create pids paths
file { "/var/praekelt/txtalert/tmp/pids/":
    ensure => "directory",
    owner => "ubuntu",
    subscribe => File['/var/praekelt/txtalert/tmp/'],
}

# Postgres role
postgres::role { "txtalert":
    ensure => present,
    password => txtalert,
    subscribe => Package["postgresql"],
}

# Postgres database
postgres::database { "txtalert_dev":
    ensure => present,
    owner => txtalert,
    template => "template0",
}

file { "/etc/nginx/sites-enabled/development.txtalert.conf":
    ensure => symlink,
    target => "/var/praekelt/txtalert/config/nginx/development.conf",
    subscribe => [
        Exec['clone_repo'],
        Package['nginx'],
    ]
}

file { "/etc/nginx/sites-enabled/default":
    ensure => absent,
}

file { "/etc/supervisor/conf.d/supervisord.develop.conf":
    ensure => symlink,
    target => "/var/praekelt/txtalert/supervisord.develop.conf",
    subscribe => [
        Exec['clone_repo'],
        Package['supervisor']
    ]
}

exec { 'create_virtualenv':
    command => 'virtualenv --no-site-packages ve',
    cwd => '/var/praekelt/txtalert',
    unless => 'test -d /var/praekelt/txtalert/ve',
    subscribe => [
        Package['python-virtualenv'],
        Exec['clone_repo'],
    ]
}

exec { 'install_packages':
    command => 'pip -E ./ve/ install -r requirements.pip',
    cwd => '/var/praekelt/txtalert',
    subscribe => Exec['create_virtualenv']
}

# Bugfix for https://bitbucket.org/jespern/django-piston/issue/173/
file { "piston_bugfix_173":
    path => "/var/praekelt/txtalert/ve/lib/python2.6/site-packages/piston/__init__.py",
    ensure => "file",
    owner => "ubuntu",
    subscribe => Exec['install_packages']
}
