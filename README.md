# python-pfgen

Puppetfile generator

## config file

pfgen.configs

```
[github]
token =  GITHUB_PAT_HERE
debug=false

[jordiprats]
skip-forked-repos=true
repo-pattern="eyp-"
current-version=True

[nttcom-ms]
skip-forked-repos=true
repo-pattern="eyp-"
current-version=True

[puppetlabs/puppetlabs-stdlib]
version=1.2.3

[eyp/eyp-demo]
url = 'ssh://git@gitlab.demo.systemadmin.es:7999/eyp/eyp-demo.git'
```
