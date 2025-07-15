# Šeštadieninės informatikos olimpiadininkų mokyklos (ŠIOM) sistema

## Sistemos vystymas

Norint dirbti su sistema lokaliai, galima tą daryti pasileidus ją Docker konteineryje. Naudojant Visual Studio Code programą viskas turėtų pasileisti be papildomo darbo naudojant [remote containers](https://code.visualstudio.com/docs/remote/containers). Su kitomis programavimo aplinkomis tikriausiai galima pasiekti panašių rezultatų, tačiau jos nėra išbandytos.

### Darbo su Visual Studio Code pradžia

* Atsidaryti šios repozitorijos direktoriją (`File -> Open Folder...`)
* Įsirašyti [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) papildinį
* Paleisti komandą `Dev Containers: Rebuild and Reopen in Container`
* Atsidaryti `http://localhost:8000` naršyklėje

### Pavyzdinių duomenų sukūrimas

Dirbant su sistema lokaliai, visi duomenys, kurie yra rašomi į duomenų bazę, bus išsaugomi *Docker volume* ir bus pasiekiami kiekvieną karta pasileidus sistemą (t.y. jie neišsitrins uždarius Visual Studio Code). Pirmą kartą pasileidžiant sistemą duomenų bazė bus užpildoma pavyzdiniais duomenimis (angl. *seed data*), kurie yra aprašyti faile `.devcontainer/seed_data/db.json`. Norint šiuos pradinius duomenis pakoreguoti, galima tai padaryti rankomis, tačiau patogiau būtų daryti taip:

* Pridėti ką reikia pasileidus sistemą (pvz. per administravimo langą)
* Paleisti šią komandą:
  ```
  python manage.py dumpdata -o .devcontainer/seed_data/db.json --indent 4 siom auth.user
  ```

Taip visa dabartinė duomenų bazės būsena bus išsaugota faile `db.json` ir kitą kartą paleidžiant programą šie duomenys bus užkrauti. Duomenys užkraunami su komanda `python manage.py loaddata .devcontainer/seed_data/db.json`, tačiau tai įvyksta automatiškai pasileidžiant sistemą.

### Duomenų bazės perkrovimas

Jei norite visiškai išvalyti lokalioje duomenų bazėje esančius duomenis, atlikite šiuos veiksmus:

* Atsidarykite repozitoriją lokaliai, o ne konteinerio viduje (`Dev Containers: Reopen Folder Locally`)
* Palaukite kelias sekundes, kad konteineriai galėtų pabaigti darbą
* Ištrinkite konteinerius ir *volume*, kuriame yra duomenų bazės failai:
  ```
  docker rm $(docker ps -a -f name=siom_devcontainer_* -q)
  docker volume rm siom_devcontainer_mysql-data
  ```
* Iš naujo atsidarykite repozitoriją konteineryje (`Remote-Containers: Rebuild and Reopen in Container`)
