# Репозитория для командного проекта Telegram Bot Event Django

## Запуск

## шаг 1

Клонирируем, самого ботa в директорию


[ссылка на бота](https://github.com/manilotw/telegram-bot-event.git)

```
"git clone ссылка_на_бота"
```

после чего она должна выглядить так:

Общая директория
1. bot/                  ---> Здесь директория клонированного бота
1.1  bot.py              ---> Здесь сам файл бота
2. backend/
2.2...                       ---> Здесь, собственно, сам бот
4. ...                       ---> Все остальное



## шаг 2

Ну, здесь, господа, кому как душа велит: хотите создавйте виртуалку хотите пользуйтесь памятью своего аппарта напрямую

Но если решите все-таки через виртуалку, то введите:

1.
 ```
python3 -m venv env
  ```
2. для владельцев яблока:
```
source env/bin/activate
```
Для владельцев окна:
 ```
 . env\scripts\activate
```

## шаг 3
Создаем базу данных 

Все легко, просто введите:

1.
```
 . python manage.py makemigrations 
```

###!Этеншн:
Перейдите только в правильную директорию перед 🙄
```
cd path/bot_backend
```

2.
```
 . python manage.py migrate
```

## шаг 4

Ребят, Мы почти у цели:

Запускаем бота:

```
 . python bot/bot.py
```

Если все ок, то никаких ошибок быть не должно
Осталось только протестить нашего с Вами бота

И как Вы уже могли догадаться, на данном этапе инфу Вам бот не даст - ее просто-напросто нет.
Поэтому

1.
```
python manage.py createsuperuser
```
2. Переход в панель админа и добавляем инфу и сохраняем

3. Снова запускаем бот и чудо должно случиться, если все пошло по плану

