# PDF Generation Service (Flask Version)

Сервис для генерации PDF-документов из JSON-данных по шаблонам для ФГИС ОПВК.

## Описание

Данный сервис предназначен для генерации PDF-документов на основе шаблонов и данных в формате JSON. Сервис разработан в рамках цифровизации процессов ФГИС ОПВК (Федеральная государственная информационная система учета и контроля за обращением с отходами I и II классов опасности).

Сервис поддерживает:
- Генерацию PDF-документов из JSON-данных
- Использование шаблонов HTML с поддержкой Jinja2
- Вставку переменных, условные блоки и циклы в шаблонах
- Генерацию QR-кодов для проверки подлинности документов
- REST API для интеграции с другими системами

## Технологии

- **Backend**: Python, Flask
- **Шаблонизация**: Jinja2
- **Генерация PDF**: WeasyPrint
- **QR-коды**: qrcode

## Структура проекта

```
pdf_service_flask/
├── api/
│   └── pdf_generator.py
├── examples/
│   ├── waste_removal_request_example.json
│   └── waste_transfer_act_example.json
├── templates/
│   ├── verification.html
│   ├── waste_removal_request.html
│   └── waste_transfer_act.html
├── utils/
│   ├── helpers.py
│   └── qr_code.py
├── app.py
├── requirements.txt
└── test_service.py
```

## Установка и запуск

### Требования

- Python 3.x
- pip

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск сервиса

```bash
python app.py
```

Сервис будет доступен по адресу: http://localhost:8000

## API Endpoints

### Генерация PDF

#### Акт приема-передачи отходов

```
POST /api/v1/waste-transfer-act
```

Пример запроса:
```json
{
  "act_number": "АКТ-2025-04-18-001",
  "act_date": "18.04.2025",
  "sender": {
    "name": "ООО \"ЭкоТранс\"",
    "inn": "7712345678",
    "address": "123456, г. Москва, ул. Промышленная, д. 10",
    "representative": {
      "name": "Иванов И.И.",
      "position": "Начальник отдела логистики"
    }
  },
  "receiver": {
    "name": "АО \"ЭкоПереработка\"",
    "inn": "7787654321",
    "address": "654321, г. Москва, ул. Заводская, д. 5",
    "representative": {
      "name": "Петров П.П.",
      "position": "Директор по производству"
    }
  },
  "contract": {
    "number": "ЭТ-2025-001",
    "date": "10.01.2025"
  },
  "transport": {
    "type": "КАМАЗ 65115",
    "number": "А123БВ77",
    "driver": "Сидоров С.С."
  },
  "wastes": [
    {
      "name": "Отработанные ртутные лампы",
      "code": "4 71 101 01 52 1",
      "hazard_class": "I",
      "quantity": 50.5,
      "packaging": "Специальный контейнер"
    },
    {
      "name": "Отработанные аккумуляторы свинцовые",
      "code": "9 20 110 01 53 2",
      "hazard_class": "II",
      "quantity": 120.0,
      "packaging": "Пластиковый контейнер"
    }
  ],
  "additional_info": "Транспортировка осуществлена в соответствии с требованиями безопасности",
  "include_qr": true
}
```

#### Заявка на вывоз отходов

```
POST /api/v1/waste-removal-request
```

Пример запроса:
```json
{
  "request_number": "ЗВО-2025-04-18-002",
  "request_date": "18.04.2025",
  "requester": {
    "name": "ООО \"ПромТех\"",
    "inn": "7723456789",
    "address": "123789, г. Москва, пр. Индустриальный, д. 15",
    "contact_person": "Смирнов А.В.",
    "phone": "+7 (495) 123-45-67",
    "representative": {
      "name": "Смирнов А.В.",
      "position": "Главный инженер"
    }
  },
  "contract": {
    "number": "ФЭО-2025-042",
    "date": "15.02.2025"
  },
  "pickup_address": "123789, г. Москва, пр. Индустриальный, д. 15, склад №3",
  "preferred_date": "25.04.2025",
  "preferred_time": "10:00-14:00",
  "wastes": [
    {
      "name": "Кислота аккумуляторная серная отработанная",
      "code": "9 20 210 01 10 2",
      "hazard_class": "II",
      "quantity": 200.0,
      "packaging": "Пластиковые канистры"
    },
    {
      "name": "Отходы конденсаторов с трихлордифенилом",
      "code": "4 72 110 00 52 2",
      "hazard_class": "II",
      "quantity": 45.5,
      "packaging": "Металлические контейнеры"
    }
  ],
  "status": "Одобрена",
  "special_requirements": "Необходимо обеспечить наличие погрузочной техники",
  "additional_info": "Доступ на территорию по предварительному согласованию",
  "operator": {
    "name": "Николаев Н.Н.",
    "position": "Оператор ФГИС ОПВК"
  },
  "approval_date": "20.04.2025",
  "include_qr": true
}
```

### Проверка подлинности документа

```
GET /verify/{qr_data}
```

## Тестирование

Для тестирования сервиса используйте скрипт `test_service.py`:

```bash
python test_service.py
```

## Расширение функциональности

### Добавление новых шаблонов

1. Создайте HTML-шаблон в директории `templates/`
2. Добавьте новый endpoint в `app.py`
3. Создайте пример JSON-данных в директории `examples/`

### Настройка шаблонов

Шаблоны используют синтаксис Jinja2:
- Вставка переменных: `{{ variable_name }}`
- Условные блоки: `{% if condition %}...{% endif %}`
- Циклы: `{% for item in items %}...{% endfor %}`

## Лицензия

Открытая лицензия
