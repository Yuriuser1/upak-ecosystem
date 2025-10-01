# 🚀 UPAK Backend Deployment Guide

## Что было добавлено

### Новые эндпоинты для личного кабинета:

1. **GET /me** - информация о текущем пользователе и подписке
   - Возвращает: `{ email, subscription_type, subscription_expires, cards_limit, cards_used }`

2. **GET /cards?limit=&offset=** - список карточек пользователя
   - Возвращает: `[{ id, title, created_at, pdf_url }]`

3. **GET /payments?limit=** - список платежей пользователя
   - Возвращает: `[{ id, amount, status, subscription_type, created_at }]`

4. **POST /payments/create** - создание платежа
   - Принимает: `{ package: 'start'|'pro' }`
   - Возвращает: `{ confirmation_url }` (редирект на ЮKassa)

Все эндпоинты защищены JWT аутентификацией через `Authorization: Bearer <token>`.

## 📋 Pull Request

**PR #3**: https://github.com/Yuriuser1/upak-ecosystem/pull/3

Пожалуйста, проверьте и смержите PR перед деплоем.

## 🔧 Деплой на сервер

### Вариант 1: Автоматический деплой (рекомендуется)

```bash
# Подключитесь к серверу
ssh -i /home/ubuntu/upak_deploy_key upak@51.250.110.59

# Скопируйте и запустите скрипт деплоя
cd /home/upak/upak-ecosystem
curl -o deploy.sh https://raw.githubusercontent.com/Yuriuser1/upak-ecosystem/feat/lk_endpoints/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Вариант 2: Ручной деплой

```bash
# 1. Подключитесь к серверу
ssh -i /home/ubuntu/upak_deploy_key upak@51.250.110.59

# 2. Перейдите в директорию проекта
cd /home/upak/upak-ecosystem

# 3. Получите последние изменения
git fetch origin
git checkout main
git merge origin/feat/lk_endpoints

# 4. Установите новые зависимости
pip3 install --user PyJWT==2.8.0 bcrypt==4.1.2

# 5. Инициализируйте базу данных
python3 init_db.py

# 6. Перезапустите сервис
sudo systemctl restart upak.service

# 7. Проверьте статус
sudo systemctl status upak.service
```

## 🧪 Тестирование

### 1. Создайте тестового пользователя

```bash
# На сервере
cd /home/upak/upak-ecosystem
python3 test_endpoints.py
```

### 2. Тестирование через curl

```bash
# Регистрация
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@upak.space","password":"StrongPass123"}'

# Получение токена
TOKEN=$(curl -X POST http://localhost:5000/auth/token \
  -d "username=test@upak.space&password=StrongPass123" | jq -r '.access_token')

# Проверка /me
curl http://localhost:5000/me \
  -H "Authorization: Bearer $TOKEN"

# Проверка /cards
curl http://localhost:5000/cards?limit=10 \
  -H "Authorization: Bearer $TOKEN"

# Проверка /payments
curl http://localhost:5000/payments?limit=10 \
  -H "Authorization: Bearer $TOKEN"

# Создание платежа
curl -X POST http://localhost:5000/payments/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"package":"start"}'
```

## 🔐 Переменные окружения

Убедитесь, что в файле `.env` на сервере установлены следующие переменные:

```bash
# JWT секрет (ОБЯЗАТЕЛЬНО изменить в продакшене!)
JWT_SECRET=your-super-secret-jwt-key-change-me

# База данных
DATABASE_URL=sqlite:////var/lib/upak/upak.db

# ЮKassa (для продакшена)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# Flask
PORT=5000
DEBUG=False
```

## 📊 Структура базы данных

После запуска `init_db.py` будут созданы следующие таблицы:

- **users** - пользователи с JWT аутентификацией
- **payments** - платежи пользователей
- **cards** - карточки товаров пользователей
- **orders** - заказы (обратная совместимость)
- **pro_subscriptions** - Pro подписки

## 🔍 Проверка логов

```bash
# Просмотр логов сервиса
sudo journalctl -u upak.service -f

# Последние 100 строк
sudo journalctl -u upak.service -n 100

# Логи с ошибками
sudo journalctl -u upak.service -p err
```

## ⚠️ Важные замечания

1. **JWT_SECRET**: Обязательно измените значение по умолчанию в продакшене!
2. **База данных**: Убедитесь, что путь к БД существует и доступен для записи
3. **Бэкапы**: Сделайте бэкап базы данных перед миграцией
4. **CORS**: Если фронтенд на другом домене, настройте CORS в Flask

## 🐛 Troubleshooting

### Проблема: Сервис не запускается

```bash
# Проверьте логи
sudo journalctl -u upak.service -n 50

# Проверьте синтаксис Python
python3 -m py_compile app.py

# Проверьте зависимости
pip3 list | grep -E "PyJWT|bcrypt"
```

### Проблема: 401 Unauthorized

- Проверьте, что токен передается в заголовке `Authorization: Bearer <token>`
- Убедитесь, что JWT_SECRET одинаковый при создании и проверке токена
- Проверьте срок действия токена (по умолчанию 7 дней)

### Проблема: База данных не найдена

```bash
# Создайте директорию для БД
sudo mkdir -p /var/lib/upak
sudo chown upak:upak /var/lib/upak

# Запустите инициализацию
python3 init_db.py
```

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте PR: https://github.com/Yuriuser1/upak-ecosystem/pull/3
2. Проверьте логи сервиса
3. Запустите тесты: `python3 test_endpoints.py`

## ✅ Чеклист деплоя

- [ ] PR #3 смержен в main
- [ ] Подключились к серверу
- [ ] Получили последние изменения из git
- [ ] Установили новые зависимости (PyJWT, bcrypt)
- [ ] Запустили init_db.py
- [ ] Настроили переменные окружения (.env)
- [ ] Перезапустили сервис
- [ ] Проверили статус сервиса
- [ ] Протестировали эндпоинты
- [ ] Проверили логи на ошибки

---

**Готово!** 🎉 Личный кабинет UPAK развернут и готов к работе!
