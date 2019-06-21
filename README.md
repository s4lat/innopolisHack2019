# innopolisHack2019
## Заказчик Максим
### PDF с описанием - [link](https://github.com/s4lat/innopolisHack2019/blob/master/Описание.pdf)

Клонируете репозиторий: 
```
$ git clone https://github.com/s4lat/innoHack2019
```

Собираете образ с помощью Dockerfile'а:
```
$ docker build --no-cache -t s4lat/innohack19 .
```
Запускаете контейнер с образом:
```
$ docker run -p 8888:8000 s4lat/innohack19
```
