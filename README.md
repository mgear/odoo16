# simbioz_config

- create an ssh-key to connect gitlab.simbioz.com.ua with the command:
```
ssh-keygen -t rsa -b 4096 -C "COMMENT"
```
- put the content of the public key in the ssh key in the ssh section in the gitlab profile:
```
https://gitlab.simbioz.com.ua/-/profile/keys
```
- for an empty project - use this command to clone the repository with all submodules over ssh:
```
git clone --recurse-submodules git@gitlab.simbioz.com.ua:NAMESPACE/PROJEECTNAME.git
```
- By default, clone submodules do checkout to the latest commit in the main project, you can switch to the main branch:
```
git submodule foreach -q --recursive 'branch="$(git config -f $toplevel/.gitmodules submodule.$name.branch)"; git checkout $branch'
```
- update the code for all submodules (remember that after this you will switch back to the latest commit branch of the main project):
```
git submodule update --recursive --remote
```
- for remove submodule use and then remove folder:
```
git rm -r --cached PATH
```
- for add submodule repo use:
```
git submodule add -b main git@gitlab.simbioz.com.ua:NAMESPACE/PROJEECTNAME.git FULL_PATH
```

**after create fork for new project, rename file .gitmodules.env to .gitmodules and and leave only the necessary repositories:**
1. only odoo modules:
```
[submodule "odoo"]
	path = odoo
	url = ../../simbioz_v17/odoo.git
	branch = main
```
