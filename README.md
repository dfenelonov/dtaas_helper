# dtaas_helper
## Помощник клиентского менеджера

Для работы с ботом необходимо в файле окружения (.env) прописать:
- BOT_TOKEN — ключ-токен телеграм бота
- GIGACHAT_CREDENTIALS — Client Secret GigachatAPI
- OPENAI_API_KEY

В `conf/config.conf`-файле:
- db_path — путь до базы данных, куда пишется история сообщений
- path_to_vectorized_db — путь до векторного хранилища
- path_to_data — путь до данных
- sys_message — системный промпт
- prompt — шаблон сообщения
- greeting — ответ бота на команду `/start`
- error_response — ответ бота на ошибку

## Описание работы
В директории dtaas_bot:
- db_manager.py — работа с БД
- db.py — обработчик db_manager
- llm_handler.py — обработчик сообщений с помощью LLM
- preprocessor.py — обработчик данных
- vec_base_manager.py — обработчки векторной базы данных
- rebase.py - скрипт для перезалива векторного хранилища, запускается командой:
`pyhton3 rebase.py --source=[PATH_TO_DATA] --to=[PATH_TO_VDB]`
