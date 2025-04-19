document.addEventListener('DOMContentLoaded', function() {
    // Handle text form submission
    document.getElementById('submitText').addEventListener('click', function(e) {
        e.preventDefault();
        processTextInput();
    });

    // Handle file form submission
    document.getElementById('submitFile').addEventListener('click', function(e) {
        e.preventDefault();
        processFileInput();
    });
});

function processTextInput() {
    const jsonText = document.getElementById('jsonText').value.trim();
    
    if (!jsonText) {
        alert('Пожалуйста, введите JSON текст');
        return;
    }

    try {
        const jsonObj = JSON.parse(jsonText);
        sendToFlask(jsonObj, 'text');
    } catch (error) {
        alert('Ошибка в JSON: ' + error.message);
        console.error('Invalid JSON:', error);
    }
}

function processFileInput() {
    const fileInput = document.getElementById('jsonFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Пожалуйста, выберите файл');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const jsonObj = JSON.parse(e.target.result);
            sendToFlask(jsonObj, 'file');
        } catch (error) {
            alert('Ошибка в JSON файле: ' + error.message);
            console.error('Invalid JSON in file:', error);
        }
    };
    reader.onerror = function() {
        alert('Ошибка при чтении файла');
    };
    reader.readAsText(file);
}

function sendToFlask(jsonData, dataType) {
    // Show loading state
    const submitBtn = dataType === 'text' 
        ? document.getElementById('submitText') 
        : document.getElementById('submitFile');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Отправка...';
    submitBtn.disabled = true;

    fetch('/api/process-json', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            data: jsonData,
            type: dataType,
            filename: dataType === 'file' ? document.getElementById('jsonFile').files[0].name : null
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message || 'Ошибка сервера'); });
        }
        return response.json();
    })
    .then(data => {
        alert('Успешно: ' + (data.message || 'Данные обработаны'));
        console.log('Server response:', data);
        // You can process the response data here
    })
    .catch(error => {
        alert('Ошибка: ' + error.message);
        console.error('Error:', error);
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}