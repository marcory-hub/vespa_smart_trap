**One-line purpose:** 
**Short summary:**
**SoT:**
**Agent:** 
**Main Index:**

---


Naar master gaan om verder te werken
```sh
  git checkout master
```
Naar demo gaan
```sh
git checkout demo
```

Een commit terug gaan
```sh
git reset --hard HEAD~1
```

Branch maken van demo
```sh
git checkout -b demo
```
push to repo
```sh
git push -u origin demo
```
geef lijst van alle branches
```sh
   git branch -a
```

pull request voor demo
```sh
https://github.com/vespCV/vespcv/pull/new/demo
```

git config --global user.name "marcory-hub"
git config --global user.email "marcory-hub@users.noreply.github.com"
```sh
git config --global user.name "marcory-hub"
git config --global user.email "marcory-hub@users.noreply.github.com"
```

---

After sync from himax main
Add the upstream (himax) repo once, then fetch and merge to origin (my fork)
```sh
cd /Users/md/Developer/vespa_smart_trap/himax_fork
git remote add upstream https://github.com/HimaxWiseEyePlus/Seeed_Grove_Vision_AI_Module_V2.git
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```
then bring it to working branch
```sh
git checkout yolo11-vespa
git merge main
# fix conflicts if any, then:
git push origin yolo11-vespa
```
