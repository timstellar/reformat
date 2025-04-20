import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const IndexPage = () => {
  const [formData, setFormData] = useState({
    // General Information
    request_number: '',
    request_date: '',
    
    // Requester Information
    requester_name: '',
    requester_inn: '',
    requester_address: '',
    requester_contact_person: '',
    requester_phone: '',
    representative_name: '',
    representative_position: '',
    
    // Contract Information
    contract_number: '',
    contract_date: '',
    
    // Pickup Details
    pickup_address: '',
    preferred_date: '',
    preferred_time: '',
    
    // Waste Specifications
    wastes: [{
      waste_code: '',
      waste_name: '',
      hazard_class: '',
      packaging_type: '',
      quantity: '',
      units: 'кг',
      notes: ''
    }],
    
    // Additional Information
    special_requirements: '',
    additional_info: '',
    qr_url: ''
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleWasteChange = (index, e) => {
    const { name, value } = e.target;
    const updatedWastes = [...formData.wastes];
    updatedWastes[index] = {
      ...updatedWastes[index],
      [name]: value
    };
    setFormData(prev => ({ ...prev, wastes: updatedWastes }));
  };

  const addWaste = () => {
    setFormData(prev => ({
      ...prev,
      wastes: [
        ...prev.wastes,
        {
          waste_code: '',
          waste_name: '',
          hazard_class: '',
          packaging_type: '',
          quantity: '',
          units: 'кг',
          notes: ''
        }
      ]
    }));
  };

  const removeWaste = (index) => {
    if (formData.wastes.length <= 1) return;
    const updatedWastes = formData.wastes.filter((_, i) => i !== index);
    setFormData(prev => ({ ...prev, wastes: updatedWastes }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Convert dates to ISO strings if needed
    const payload = {
      ...formData,
      request_date: formData.request_date ? new Date(formData.request_date).toISOString() : null,
      contract_date: formData.contract_date ? new Date(formData.contract_date).toISOString() : null,
      preferred_date: formData.preferred_date ? new Date(formData.preferred_date).toISOString() : null
    };

    const { success, data, error: submissionError } = await submitWasteRequest(payload);

    if (success) {
      // Handle successful response
      console.log('API Response:', data);
      
      // Navigate to download page with the file ID
      navigate(`/download/${data.fileId}`, {
        state: {
          fileName: data.fileName || 'waste_removal_request.pdf'
        }
      });
    } else {
      setError(submissionError);
    }

    setIsSubmitting(false);
  };

  return (
    <div className="page">
      <h1>Создание заявки на вывоз отходов I и II классов опасности</h1>

      <form onSubmit={handleSubmit} className="waste-form">
        {/* General Information */}
        <fieldset>
          <legend>Общая информация</legend>
          <div className="form-group">
            <label htmlFor="request_number">Номер заявки:</label>
            <input
              type="text"
              id="request_number"
              name="request_number"
              value={formData.request_number}
              onChange={handleChange}
              required
              placeholder="Пример: ЗВО-2025-04-18-002"
            />
          </div>
          <div className="form-group">
            <label htmlFor="request_date">Дата заявки:</label>
            <input
              type="date"
              id="request_date"
              name="request_date"
              value={formData.request_date}
              onChange={handleChange}
              required
            />
          </div>
        </fieldset>

        {/* Requester Information */}
        <fieldset>
          <legend>Заявитель</legend>
          <div className="form-group">
            <label htmlFor="requester_name">Наименование:</label>
            <input
              type="text"
              id="requester_name"
              name="requester_name"
              value={formData.requester_name}
              onChange={handleChange}
              required
              placeholder='ООО "ПромТех"'
            />
          </div>
          <div className="form-group">
            <label htmlFor="requester_inn">ИНН:</label>
            <input
              type="text"
              id="requester_inn"
              name="requester_inn"
              value={formData.requester_inn}
              onChange={handleChange}
              required
              pattern="\d{10}|\d{12}"
              title="Введите 10 или 12 цифр ИНН"
              placeholder="7723456789"
            />
          </div>
          <div className="form-group">
            <label htmlFor="requester_address">Юридический адрес:</label>
            <textarea
              id="requester_address"
              name="requester_address"
              value={formData.requester_address}
              onChange={handleChange}
              rows="2"
              required
              placeholder="123789, г. Москва, пр. Индустриальный, д. 15"
            />
          </div>
          <div className="form-group">
            <label htmlFor="requester_contact_person">Контактное лицо (ФИО):</label>
            <input
              type="text"
              id="requester_contact_person"
              name="requester_contact_person"
              value={formData.requester_contact_person}
              onChange={handleChange}
              required
              placeholder="Смирнов А.В."
            />
          </div>
          <div className="form-group">
            <label htmlFor="requester_phone">Телефон:</label>
            <input
              type="tel"
              id="requester_phone"
              name="requester_phone"
              value={formData.requester_phone}
              onChange={handleChange}
              required
              placeholder="+7 (495) 123-45-67"
            />
          </div>

          {/* Representative */}
          <fieldset className="nested-fieldset">
            <legend>Представитель Заявителя (для подписи)</legend>
            <div className="form-group">
              <label htmlFor="representative_name">ФИО представителя:</label>
              <input
                type="text"
                id="representative_name"
                name="representative_name"
                value={formData.representative_name}
                onChange={handleChange}
                required
                placeholder="Смирнов А.В."
              />
            </div>
            <div className="form-group">
              <label htmlFor="representative_position">Должность представителя:</label>
              <input
                type="text"
                id="representative_position"
                name="representative_position"
                value={formData.representative_position}
                onChange={handleChange}
                required
                placeholder="Главный инженер"
              />
            </div>
          </fieldset>
        </fieldset>

        {/* Contract Information */}
        <fieldset>
          <legend>Договор</legend>
          <div className="form-group">
            <label htmlFor="contract_number">Номер договора:</label>
            <input
              type="text"
              id="contract_number"
              name="contract_number"
              value={formData.contract_number}
              onChange={handleChange}
              required
              placeholder="ФЭО-2025-042"
            />
          </div>
          <div className="form-group">
            <label htmlFor="contract_date">Дата договора:</label>
            <input
              type="date"
              id="contract_date"
              name="contract_date"
              value={formData.contract_date}
              onChange={handleChange}
              required
            />
          </div>
        </fieldset>

        {/* Pickup Details */}
        <fieldset>
          <legend>Детали Вывоза</legend>
          <div className="form-group">
            <label htmlFor="pickup_address">Адрес места накопления (вывоза):</label>
            <textarea
              id="pickup_address"
              name="pickup_address"
              value={formData.pickup_address}
              onChange={handleChange}
              rows="2"
              required
              placeholder="123789, г. Москва, пр. Индустриальный, д. 15, склад №3"
            />
          </div>
          <div className="form-group">
            <label htmlFor="preferred_date">Желаемая дата вывоза:</label>
            <input
              type="date"
              id="preferred_date"
              name="preferred_date"
              value={formData.preferred_date}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="preferred_time">Желаемое время вывоза:</label>
            <input
              type="text"
              id="preferred_time"
              name="preferred_time"
              value={formData.preferred_time}
              onChange={handleChange}
              required
              placeholder="Пример: 10:00-14:00"
            />
          </div>
        </fieldset>

        {/* Waste Specifications */}
        <fieldset>
          <legend>Спецификация Отходов</legend>
          {formData.wastes.map((waste, index) => (
            <div key={index} className="waste-row">
              <div className="form-group">
                <label htmlFor={`waste_code_${index}`}>Код отхода:</label>
                <input
                  type="text"
                  id={`waste_code_${index}`}
                  name="waste_code"
                  value={waste.waste_code}
                  onChange={(e) => handleWasteChange(index, e)}
                  required
                  placeholder="Код ФККО"
                />
              </div>
              <div className="form-group">
                <label htmlFor={`waste_name_${index}`}>Наименование отхода:</label>
                <input
                  type="text"
                  id={`waste_name_${index}`}
                  name="waste_name"
                  value={waste.waste_name}
                  onChange={(e) => handleWasteChange(index, e)}
                  required
                  placeholder="Полное наименование"
                />
              </div>
              <div className="form-group">
                <label htmlFor={`hazard_class_${index}`}>Класс опасности:</label>
                <select
                  id={`hazard_class_${index}`}
                  name="hazard_class"
                  value={waste.hazard_class}
                  onChange={(e) => handleWasteChange(index, e)}
                  required
                >
                  <option value="">Выберите класс</option>
                  <option value="I">I класс</option>
                  <option value="II">II класс</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor={`packaging_type_${index}`}>Тара/упаковка:</label>
                <input
                  type="text"
                  id={`packaging_type_${index}`}
                  name="packaging_type"
                  value={waste.packaging_type}
                  onChange={(e) => handleWasteChange(index, e)}
                  required
                  placeholder="Пример: Металлическая бочка"
                />
              </div>
              <div className="form-group">
                <label htmlFor={`quantity_${index}`}>Количество:</label>
                <div className="quantity-group">
                  <input
                    type="number"
                    id={`quantity_${index}`}
                    name="quantity"
                    value={waste.quantity}
                    onChange={(e) => handleWasteChange(index, e)}
                    required
                    min="0"
                    step="0.01"
                  />
                  <select
                    name="units"
                    value={waste.units}
                    onChange={(e) => handleWasteChange(index, e)}
                  >
                    <option value="кг">кг</option>
                    <option value="т">т</option>
                    <option value="л">л</option>
                    <option value="м³">м³</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor={`notes_${index}`}>Примечания:</label>
                <input
                  type="text"
                  id={`notes_${index}`}
                  name="notes"
                  value={waste.notes}
                  onChange={(e) => handleWasteChange(index, e)}
                  placeholder="Дополнительная информация"
                />
              </div>
              {formData.wastes.length > 1 && (
                <button
                  type="button"
                  className="remove-waste-btn"
                  onClick={() => removeWaste(index)}
                >
                  Удалить
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            id="addWasteBtn"
            className="add-waste-btn"
            onClick={addWaste}
          >
            Добавить отход
          </button>
        </fieldset>

        {/* Additional Information */}
        <fieldset>
          <legend>Дополнительная информация и QR-код</legend>
          <div className="form-group">
            <label htmlFor="special_requirements">Особые требования к вывозу:</label>
            <textarea
              id="special_requirements"
              name="special_requirements"
              value={formData.special_requirements}
              onChange={handleChange}
              rows="3"
              placeholder="Пример: Необходимо обеспечить наличие погрузочной техники"
            />
          </div>
          <div className="form-group">
            <label htmlFor="additional_info">Прочая информация:</label>
            <textarea
              id="additional_info"
              name="additional_info"
              value={formData.additional_info}
              onChange={handleChange}
              rows="3"
              placeholder="Пример: Доступ на территорию по предварительному согласованию"
            />
          </div>
          <div className="form-group">
            <label htmlFor="qr_url">URL для QR-кода (необязательно):</label>
            <input
              type="url"
              id="qr_url"
              name="qr_url"
              value={formData.qr_url}
              onChange={handleChange}
              placeholder="https://example.com/verify/..."
            />
            <small>Если указать URL, в PDF будет добавлен QR-код, ведущий на эту страницу.</small>
          </div>
        </fieldset>

        {/* Submit Button */}
        <div className="submit-area">
          <button type="submit" id="generatePdfBtn">
            Сгенерировать и скачать PDF
          </button>
        </div>
      </form>
    </div>
  );
};

export default IndexPage;