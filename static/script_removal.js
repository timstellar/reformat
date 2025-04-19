// Ждем, пока весь HTML документ будет загружен и готов к работе
document.addEventListener('DOMContentLoaded', () => {

    // Находим основные элементы на странице
    const form = document.getElementById('wasteRemovalForm');
    const addWasteBtn = document.getElementById('addWasteBtn');
    const wastesContainer = document.getElementById('wastesContainer');
    // Находим кнопку отправки (используем id из обновленного HTML)
    const generatePdfBtn = document.getElementById('generatePdfBtn');
    // Находим div для вывода сообщений пользователю
    const userMessageDiv = document.getElementById('userMessage');

    /**
     * Обработчик для кнопки "Добавить отход".
     * Создает новую строку с полями для ввода данных об одном отходе
     * и добавляет ее в контейнер wastesContainer.
     * Также добавляет кнопку "Удалить" для этой строки.
     */
    addWasteBtn.addEventListener('click', () => {
        // Создаем новый div-контейнер для полей одного отхода
        const wasteEntryDiv = document.createElement('div');
        wasteEntryDiv.classList.add('waste-entry'); // Добавляем класс для стилизации и поиска

        // Заполняем div необходимыми полями ввода и кнопкой удаления
        // Используем data-атрибуты для более надежного поиска элементов внутри строки
        wasteEntryDiv.innerHTML = `
            <input type="text" name="waste_name" data-field="name" placeholder="Наименование Отхода" required>
            <input type="text" name="waste_code" data-field="code" placeholder="Код ФККО" required pattern="[0-9 ]{15}" title="Введите код ФККО (11 цифр и пробелы, всего 15 симв.)">
            <select name="waste_hazard_class" data-field="hazard_class" required>
                <option value="" disabled selected>Класс?</option>
                <option value="I">I</option>
                <option value="II">II</option>
                <!-- При необходимости можно добавить другие классы -->
            </select>
            <input type="number" step="any" min="0" name="waste_quantity" data-field="quantity" placeholder="Кол-во (кг)" required>
            <input type="text" name="waste_packaging" data-field="packaging" placeholder="Упаковка" required>
            <button type="button" class="remove-waste-btn">Удалить</button>
        `;

        // Добавляем созданный div в контейнер для отходов
        wastesContainer.appendChild(wasteEntryDiv);

        // Находим кнопку "Удалить" ВНУТРИ только что созданного div
        const removeBtn = wasteEntryDiv.querySelector('.remove-waste-btn');
        // Добавляем обработчик для этой кнопки "Удалить"
        removeBtn.addEventListener('click', (event) => {
            // Удаляем родительский div (всю строку с полями для этого отхода)
            // event.target ссылается на кнопку, closest находит ближайшего родителя с классом .waste-entry
            event.target.closest('.waste-entry').remove();
            // После удаления можно перепроверить форму или обновить какие-то итоги, если нужно
        });
    });

    /**
     * Обработчик для отправки формы (нажатия кнопки "Сгенерировать и скачать PDF").
     * Собирает данные из формы, формирует JSON, отправляет его на сервер,
     * обрабатывает ответ и инициирует скачивание PDF файла в случае успеха.
     * Использует async/await для управления асинхронными операциями.
     */
    form.addEventListener('submit', async (event) => { // Делаем функцию асинхронной (async)
        event.preventDefault(); // Предотвращаем стандартную перезагрузку страницы при отправке формы
        showMessage('', ''); // Очищаем предыдущие сообщения об ошибках или успехе

        // Блокируем кнопку и меняем текст, чтобы пользователь знал, что идет процесс
        generatePdfBtn.disabled = true;
        generatePdfBtn.textContent = 'Генерация PDF...';

        // Создаем пустой объект JavaScript, куда будем собирать данные из формы
        const formData = {};

        try { // Используем блок try...catch для централизованной обработки ошибок
            // --- Шаг 1: Сбор данных из полей формы ---

            formData.request_number = document.getElementById('request_number').value.trim();
            formData.request_date = formatDate(document.getElementById('request_date').value);

            formData.requester = {
                name: document.getElementById('requester_name').value.trim(),
                inn: document.getElementById('requester_inn').value.trim(),
                address: document.getElementById('requester_address').value.trim(),
                contact_person: document.getElementById('requester_contact_person').value.trim(),
                phone: document.getElementById('requester_phone').value.trim(),
                representative: {
                    name: document.getElementById('representative_name').value.trim(),
                    position: document.getElementById('representative_position').value.trim()
                }
            };

            formData.contract = {
                number: document.getElementById('contract_number').value.trim(),
                date: formatDate(document.getElementById('contract_date').value)
            };

            formData.pickup_address = document.getElementById('pickup_address').value.trim();
            formData.preferred_date = formatDate(document.getElementById('preferred_date').value);
            formData.preferred_time = document.getElementById('preferred_time').value.trim();

            // Собираем данные из динамически добавленных строк отходов
            formData.wastes = []; // Инициализируем массив для отходов
            const wasteEntries = wastesContainer.querySelectorAll('.waste-entry');

            // Проверяем, добавлен ли хотя бы один отход
            if (wasteEntries.length === 0) {
                 throw new Error("Необходимо добавить хотя бы один отход в спецификацию.");
            }

            // Проходим по каждой строке отхода
            wasteEntries.forEach((entryDiv, index) => {
                // Находим поля внутри текущей строки отхода
                const nameInput = entryDiv.querySelector('[data-field="name"]');
                const codeInput = entryDiv.querySelector('[data-field="code"]');
                const classSelect = entryDiv.querySelector('[data-field="hazard_class"]');
                const quantityInput = entryDiv.querySelector('[data-field="quantity"]');
                const packagingInput = entryDiv.querySelector('[data-field="packaging"]');

                // Простая валидация на заполненность обязательных полей в строке
                if (!nameInput.value.trim() || !codeInput.value.trim() || !classSelect.value || !quantityInput.value.trim() || !packagingInput.value.trim()) {
                    // Выбрасываем ошибку, если какое-то поле не заполнено
                    throw new Error(`Пожалуйста, заполните все поля для отхода №${index + 1}.`);
                }

                // Создаем объект для текущего отхода
                const wasteItem = {
                    name: nameInput.value.trim(),
                    code: codeInput.value.trim(),
                    hazard_class: classSelect.value,
                    // Преобразуем количество в число с плавающей точкой
                    quantity: parseFloat(quantityInput.value) || 0, // Если не число, будет 0
                    packaging: packagingInput.value.trim()
                };
                // Добавляем объект отхода в массив
                formData.wastes.push(wasteItem);
            });

            // Собираем необязательную дополнительную информацию
            const specialReq = document.getElementById('special_requirements').value.trim();
            if (specialReq) { // Добавляем поле, только если оно не пустое
                formData.special_requirements = specialReq;
            }

            const additionalInfo = document.getElementById('additional_info').value.trim();
            if (additionalInfo) { // Добавляем поле, только если оно не пустое
                formData.additional_info = additionalInfo;
            }

            // Получаем URL для QR-кода из формы
            const qrUrl = document.getElementById('qr_url').value.trim();
            if (qrUrl) { // Если URL введен, добавляем его в данные
                formData.qr_url = qrUrl;
                // Флаг include_qr бэкенд, похоже, не использует, но можно добавить для ясности
                // formData.include_qr = true;
            }
            // Если qr_url не введен, он просто не будет добавлен в JSON

            // --- Шаг 2: Преобразование данных в JSON ---
            const jsonString = JSON.stringify(formData, null, 2); // null, 2 для красивого форматирования (необязательно для отправки)
            // console.log("Отправляемый JSON:", jsonString); // Можно раскомментировать для отладки

            // --- Шаг 3: Отправка JSON на сервер с помощью Fetch API ---
            const apiUrl = '/api/v1/waste-removal-request'; // URL вашего API эндпоинта
            const response = await fetch(apiUrl, { // Используем await для ожидания ответа сервера
                method: 'POST',                    // Метод запроса
                headers: {
                    'Content-Type': 'application/json' // Указываем, что отправляем JSON
                    // Можно добавить другие заголовки при необходимости (например, авторизацию)
                    // 'Authorization': 'Bearer YOUR_TOKEN'
                },
                body: jsonString                   // Тело запроса - наша JSON строка
            });

            // --- Шаг 4: Обработка ответа от сервера ---
            if (response.ok) { // Проверяем, успешен ли запрос (статус 200-299)
                // Проверяем, действительно ли сервер вернул PDF
                const contentType = response.headers.get('Content-Type');
                if (contentType && contentType.includes('application/pdf')) {
                    // Получаем содержимое ответа как Blob (бинарные данные)
                    const blob = await response.blob();

                    // Создаем временный URL для этого Blob
                    const downloadUrl = window.URL.createObjectURL(blob);

                    // Создаем невидимую ссылку для инициации скачивания
                    const a = document.createElement('a');
                    a.style.display = 'none'; // Скрываем ссылку
                    a.href = downloadUrl;    // Устанавливаем URL для скачивания

                    // Формируем имя файла для скачивания, используя номер заявки
                    const downloadFilename = `Заявка_на_вывоз_${formData.request_number || 'документ'}.pdf`;
                    a.download = downloadFilename; // Устанавливаем имя файла

                    // Добавляем ссылку на страницу, "кликаем" по ней и сразу удаляем
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);

                    // Освобождаем память, удаляя созданный временный URL
                    window.URL.revokeObjectURL(downloadUrl);

                    // Показываем сообщение об успехе
                    showMessage('PDF успешно сгенерирован и скачан!', 'success');

                    // Опционально: Очистка формы после успешной отправки
                    // form.reset(); // Сбрасывает все поля формы
                    // wastesContainer.innerHTML = ''; // Очищает список добавленных отходов
                    // showMessage('', ''); // Убирает сообщение об успехе через некоторое время
                    // setTimeout(() => showMessage('', ''), 5000);

                } else {
                    // Если статус ok, но тип контента не PDF - это странная ситуация
                    throw new Error(`Сервер вернул успешный статус, но ответ не является PDF файлом. Content-Type: ${contentType}`);
                }
            } else {
                // Если статус ответа НЕ ok (например, 400 Bad Request, 500 Internal Server Error)
                let errorText = `Ошибка сервера: ${response.status} ${response.statusText}`;
                try {
                    // Пытаемся прочитать тело ответа как JSON, чтобы получить более детальную ошибку от сервера
                    const errorData = await response.json();
                    // Если в JSON есть поле 'error', используем его, иначе показываем весь JSON
                    errorText = `Ошибка: ${errorData.error || JSON.stringify(errorData)}`;
                } catch (e) {
                    // Если тело ответа не JSON или пустое, используем стандартный текст ошибки
                    console.warn("Не удалось прочитать тело ошибки как JSON:", e);
                }
                 throw new Error(errorText); // Выбрасываем ошибку, чтобы ее поймал catch блок
            }

        } catch (error) {
            // Ловим любые ошибки, возникшие в блоке try (ошибки сети, ошибки валидации, ошибки от сервера)
            console.error('Произошла ошибка при генерации PDF:', error);
            // Показываем сообщение об ошибке пользователю
            showMessage(`Не удалось сгенерировать PDF: ${error.message}`, 'error');

        } finally {
             // Блок finally выполняется всегда, независимо от того, была ошибка или нет
             // Возвращаем кнопку в исходное состояние (активна, исходный текст)
            generatePdfBtn.disabled = false;
            generatePdfBtn.textContent = 'Сгенерировать и скачать PDF';
        }
    });

    /**
     * Вспомогательная функция для форматирования даты из 'YYYY-MM-DD' (стандарт HTML5)
     * в формат 'DD.MM.YYYY' (как в примерах JSON).
     * @param {string} dateString - Дата в формате 'YYYY-MM-DD'.
     * @returns {string} - Дата в формате 'DD.MM.YYYY' или пустая строка, если входная дата пуста.
     */
    function formatDate(dateString) {
        if (!dateString) return ""; // Если дата не введена, возвращаем пустую строку
        const parts = dateString.split('-'); // Разделяем строку по дефису
        if (parts.length === 3) { // Убеждаемся, что получили три части (год, месяц, день)
            // Собираем строку в нужном формате: день.месяц.год
            return `${parts[2]}.${parts[1]}.${parts[0]}`;
        }
        // Если формат неожиданный, возвращаем исходную строку
        return dateString;
    }

    /**
     * Вспомогательная функция для отображения сообщений пользователю.
     * Управляет текстом и стилями div'а с id="userMessage".
     * @param {string} message - Текст сообщения.
     * @param {'success'|'error'|''} type - Тип сообщения ('success', 'error') или пустая строка для скрытия.
     */
    function showMessage(message, type) {
        // Устанавливаем текст сообщения
        userMessageDiv.textContent = message;
        // Сначала убираем все классы типов, чтобы не было конфликтов
        userMessageDiv.classList.remove('success', 'error');
        // Если тип указан ('success' или 'error'), добавляем соответствующий класс
        if (type) {
            userMessageDiv.classList.add(type);
            // Можно добавить автоскрытие сообщения через некоторое время
            // setTimeout(() => showMessage('', ''), 7000); // Скрыть через 7 секунд
        }
        // Если type пустой, сообщение будет скрыто (т.к. нет классов 'success' или 'error')
    }

}); // Конец обработчика DOMContentLoaded