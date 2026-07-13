# shikimori-anime-news-notifier
Скрипт для отправки новостей с сайта Shikimori в Discord через Webhook.
Периодически проверяет новые топики в разделе «Новости» и отправляет их в указанный канал с красивым оформлением 
(включая большую картинку, ссылки, YouTube-трейлеры и чистый текст).

🚀 Быстрый старт

1. Сделайте форк этого репозитория в свой аккаунт на GitHub.
2. Зайдите в нужный канал Discord → Настройки канала → Интеграции → Вебхуки.
3. Создайте вебхук и скопируйте его URL.
4. В вашем репозитории перейдите в Settings → Secrets and variables → Actions -> "New repository secret" и добавьте:
5. Name = "DISCORD_WEBHOOK_URL", Secret = "Ваш полный URL вебхука Discord"
6. Перейдите во вкладку "Actions" вашего репозитория и выбрав "Shikimori Anime News Notifier" запустите кнопкой "Run workflow" 