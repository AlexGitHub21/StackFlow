$(document).ready(function(){
    $('#form1').off('submit').on('submit', function(event) {
        event.preventDefault(); // Останавливаем стандартную отправку формы
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    var newRowId = $('#product-list tr').length+1; // Определяем новый индекс
                    // Добавляем новый товар в список без перезагрузки страницы
                    $('#product-list').append(`
                        <tr data-row_id="${newRowId}" data-product_id="${response.new_product.id}" class="text-center align-middle">
                            <td>${response.new_product.name}</td>
                            <td>${response.new_product.description}</td>
                            <td>${response.new_product.price}</td>
                            <td class="product-quantity">${response.new_product.quantity}</td>
                            <td class="product-location">${response.new_product.location_name}</td>
                            <td>
                                <button type="submit" id='save_id' data-product_id=${response.new_product.id}
                                    class="btn btn-outline-primary open-modal"
                                    data-bs-toggle="modal" title="Добавить на склад"
                                    data-bs-target="#modal3">
                                   <img src="static/images/add-button.png">
                                </button>
                            </td>
                            <td>
                                <button type="button" id='delete_prod' data-product_id=${response.new_product.id}
                                    class="btn btn-outline-primary open-modal"
                                    data-bs-toggle="modal" title="Удалить со склада"
                                    data-bs-target="#modal4">
                                   <img src="static/images/delete-button.png">
                                   </button>
                                </td>
                        </tr>
                    `);
                    var newTooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                    newTooltips.forEach(function (tooltipTriggerEl) {
                    new bootstrap.Tooltip(tooltipTriggerEl);
                    });
                    // Закрываем модальное окно
                    $('#modal1').modal('hide');
                    // Очищаем форму
                    form[0].reset();
                } else {
                    alert('Ошибка при добавлении товара');
                }
            },
            error: function() {
                alert('Произошла ошибка на сервере');
            }
        });
    });
    $('#form2').off('submit').on('submit', function(event) {
        event.preventDefault();
        var form = $(this);
        var location = $('#form2 input[name="name"]').val() || Null;
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function(response) {
                if (response.success) {
                    alert('Локация: ' + response.name + ' добавлена в БД')
                    // Закрываем модальное окно
                    $('#modal2').modal('hide');
                    // Очищаем форму
                    form[0].reset();
                    updateLocationList();
                } else {
                    alert('Такая локация уже добавлена в БД');
                }
            },
            error: function() {
                alert('Произошла ошибка на сервере');
            }

        });
    });

    // Функция для обновления списка локаций
    function updateLocationList() {
        $.ajax({
            url: '/get_locations',  // Новый маршрут для получения списка локаций
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                var locationSelect = $('#form3 select[name="location_id"]');
                locationSelect.empty();  // Очищаем старые данные

                // Добавляем обновленные локации
                response.locations.forEach(function(location) {
                    locationSelect.append($('<option>', {
                        value: location.id,
                        text: location.name
                    }));
                });

                console.log("Список локаций обновлен");
            },
            error: function() {
                console.error("Ошибка загрузки списка локаций");
            }
        });
    }

    var selectedRow;
    var productID;
    var locationID;
    var newQuantity;
    $(document).on('click', '.open-modal', function() {
//        productID = $(this).attr('data-product_id');
        productID = $(this).data('product_id');
        console.log("Clicked product ID:", productID);

        selectedRow = $(this).closest('tr');  // Сохраняем строку, в которой нажата кнопка
        $('#form3').data('selectedRow', selectedRow); // Сохраняем ссылку в data() формы
        $('#form4').data('selectedRow', selectedRow);
    });
    $('#form3').off('submit').on('submit', function(event) {
        event.preventDefault();
        selectedRow = $(this).data('selectedRow');
        locationID = parseInt($('#form3 select[name="location_id"]').val());
        var additionalQuantity = parseInt($('#form3 input[name="quantity"]').val() || 0); // Получаем quantity
        console.log("AddQuantity:", additionalQuantity)
        var currentQuantity = parseInt(selectedRow.find('.product-quantity').text() || 0); //Получаем текущее количество
        console.log("CurrentQuantity:", currentQuantity);
        var currentLocation = selectedRow.find('.product-location').text().trim();
        if (!locationID) {
            alert("Не выбрана локация")
        }
        if (productID) {
            $.ajax({
                type: 'POST',
                url: '/add_inventory',
                contentType: "application/json",
                data: JSON.stringify({ product_id: productID, location_id: locationID, quantity: additionalQuantity }),
                success: function(response) {
                    if (response.success) {
                        var newQuantity = response.new_data.newQuantity;
                        var newLocation = response.new_data.newLocation;
                        var existingRow = $('#product-list tr').filter(function() {
                            return $(this).find('.product-location').text().trim() === newLocation &&
                                    $(this).attr('data-product_id') == productID;
                        });
                        // Ситуация 1: Если нет строки с такой локацией, добавляем строку
                        if (existingRow.length === 0) {
                            // Проверяем, есть ли строки с другим товаром, но без локации (т.е. это текущий товар без локации)
                            var rowWithoutLocation = $('#product-list tr').filter(function() {
                                return $(this).attr('data-product_id') == productID &&
                                       $(this).find('.product-location').text().trim() === '';
                            });

                        // Если такая строка есть (товар без локации), обновляем её
                        if (rowWithoutLocation.length > 0) {
                            rowWithoutLocation.find('.product-location').text(newLocation);
                            rowWithoutLocation.find('.product-quantity').text(newQuantity).hide().fadeIn();
                        } else {
                            var newRowId = $('#product-list tr').length + 1;
                            $('#product-list').append(`
                                <tr data-row_id="${newRowId}" data-product_id="${productID}" class="text-center align-middle">
                                    <td>${response.new_data.name}</td>
                                    <td>${response.new_data.description}</td>
                                    <td>${response.new_data.price}</td>
                                    <td class="product-quantity">${response.new_data.newQuantity}</td>
                                    <td class="product-location">${response.new_data.newLocation}</td>
                                    <td>
                                        <button type="submit" id='save_id' data-product_id=${productID}
                                            class="btn btn-outline-primary open-modal"
                                            data-bs-toggle="modal" title="Добавить на склад"
                                            data-bs-target="#modal3">
                                           <img src="static/images/add-button.png">
                                        </button>
                                    </td>
                                    <td>
                                        <button type="button" id='delete_prod' data-product_id=${productID}
                                            class="btn btn-outline-primary open-modal"
                                            data-bs-toggle="modal" title="Удалить со склада"
                                            data-bs-target="#modal4">
                                           <img src="static/images/delete-button.png">
                                           </button>
                                        </td>
                                </tr>
                            `);
                        }
                    } else {
                    // Ситуация 2: Если строка с такой локацией есть, обновляем только количество
                        existingRow.find('.product-quantity').text(newQuantity).hide().fadeIn();
                    }

                        $('#modal3').modal('hide');
                        $('#form3')[0].reset();
                    } else {
                        alert("Ошибка обновления данных");
                    }
                }
            });
        } else {
        alert("ID товара не задан");
        }
    });

    var reduceQuantity;
    var location;
    $('#form4').off('submit').on('submit', function(event) {
        event.preventDefault(); // Останавливаем стандартную отправку формы
        selectedRow = $(this).data('selectedRow');
        reduceQuantity = parseInt($('#form4 input[name="quantity"]').val() || 0); // Получаем quantity
        console.log("ReduceQuantity:", reduceQuantity)
        location = selectedRow.find('.product-location').text(); //Получаем текущее количество
        console.log("loc", location)
        productID = selectedRow.find('.open-modal').data('product_id'); // Берем ID из кнопки

        if (productID && location && reduceQuantity > 0) {
            $.ajax({
                type: 'POST',
                url: '/reduce_quantity',
                contentType: "application/json",
                data: JSON.stringify({ product_id: productID, location: location, quantity: reduceQuantity }),
                success: function(response) {
                    if (response.success) {
                        selectedRow.find('.product-quantity').text(response.new_data.newQuantity).hide().fadeIn();
                        selectedRow.find('.product-location').text(response.new_data.newLocation).hide().fadeIn();
                        $('#modal4').modal('hide');
                        $('#form4')[0].reset();
                    } else {
                    alert("Количество товара на складе меньше указанного");
                    }
                },
                error: function() {
                    alert('Произошла ошибка на сервере');
                }
            });
        } else {
        alert("Некорректные данные");
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
});