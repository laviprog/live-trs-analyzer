# LIVE-TRS-ANALYZER

LIVE-TRS-ANALYZER – сервис, который обрабатывает поток (rtmp, hls), создает субтитры на лету, отслеживает сюжет по ключевым словам и делает суммаризацию (температура новости, ключевые моменты) с помощью ИИ. 

---

- [Начало работы](#начало-работы)
- [Запустить с помощью Docker](#запустить-с-помощью-docker)

### Начало работы

**Шаг 1**: Создать файл .env на основе подготовленного .env.example с нужными переменными 

```shell
  cp .env.example .env
```

**Шаг 2**: Добавить значения переменных окружения в .env

### Запустить с помощью Docker

```shell
  docker compose up --build -d
```
