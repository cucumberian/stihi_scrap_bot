# Stihi scrap bot
## Описание
Загрузчик для стихов автора с сайта [stihi.ru](https://stihi.ru) в виде телеграм бота.
После окончании загрузки стихов формирует csv, txt, pdf, markdown с произведениями.

## Запуск
### Docker-Compose
1. Создайте файл `.env` с токеном для телеграм бота от @BotFather в каталоге рядом с `docker-compose.yml`.
	```shell
	TEL_API_TOKEN="TELEGRAM BOT TOKEN FROM @BotFather"
	```
2. Запустите docker-compose командой:
	```shell
	docker-compose up -d
	```
## Загрузка
Отправьте боту ссылку на автора с сайта [stihi.ru](https://stihi.ru) и ждите окончания загрузки.

## Changelog
__03.09.2024__
- добавлен вывод в markdown формат
- убран excel формат
- уменьшен вывод из-за новых лимитов на общение с ботами