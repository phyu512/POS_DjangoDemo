document.addEventListener('DOMContentLoaded', function () {
    let priceMap = {};

    function updateSubtotal(row) {
        const qtyInput = row.querySelector('[name$="-quantity"]');
        const hiddenPriceInput = row.querySelector('input[name$="-price"]');
        const subtotalCell = row.querySelector('.subtotal');

        if (!qtyInput || !hiddenPriceInput || !subtotalCell) return;

        const qty = parseFloat(qtyInput.value) || 0;
        const price = parseFloat(hiddenPriceInput.value) || 0;

        const subtotal = qty * price;

        subtotalCell.textContent = subtotal.toFixed(2);

        updateTotal();
    }

    function updateTotal() {
        let total = 0;
        document.querySelectorAll('.item-row').forEach(row => {
            const subtotal = parseFloat(row.querySelector('.subtotal').textContent) || 0;
            total += subtotal;
        });
        document.getElementById('total-amount').textContent = total.toFixed(2);
    }

    priceMap = JSON.parse(
        document.getElementById('product-price-map').textContent
    );

    // Bind existing rows
    document.querySelectorAll('#items-table tbody tr.item-row').forEach(row => {
        bindRowEvents(row, priceMap);
    });

    function bindRowEvents(row, priceMap) {
        const productSelect = row.querySelector('.product-select');
        const qtyInput = row.querySelector('[name$="-quantity"]');
        const hiddenPriceInput = row.querySelector('input[name$="-price"]');
        const displayPriceInput = row.querySelector('.price-display');
        const removeBtn = row.querySelector('.remove-row');

        // ----------------------
        // 1️⃣ Initialize price from selected product
        // ----------------------
        if (productSelect) {
            const selectedProductId = productSelect.value;
            let price =0;

            if (selectedProductId && priceMap[selectedProductId] !== undefined) {
                price = parseFloat(priceMap[selectedProductId]) || 0;
            }

            hiddenPriceInput.value = price;
            displayPriceInput.value = price;

            updateSubtotal(row);
        }

        // ----------------------
        // 2️⃣ Update price when product changes
        // ----------------------
        if (productSelect) {
            productSelect.addEventListener('change', function () {
                const selectedProductId = productSelect.value;
                let price = 0;
                if (typeof priceMap !== 'undefined' && priceMap[selectedProductId] !== undefined) {
                     price = parseFloat(priceMap[selectedProductId]);
                    // update subtotal
                } else {
                    console.warn('Price not found or priceMap undefined', selectedProductId);
                    const price = 0; // safe fallback
                }

                hiddenPriceInput.value = price;
                displayPriceInput.value = price;

                updateSubtotal(row);
            });
        }

        // ----------------------
        // 3️⃣ Quantity change → update subtotal
        // ----------------------
        if (qtyInput) {
            qtyInput.addEventListener('input', function () {
                updateSubtotal(row);
            });
        }

        // ----------------------
        // 4️⃣ Remove row
        // ----------------------
        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                const deleteInput = row.querySelector('input[name$="-DELETE"]');
                if (deleteInput) {
                    deleteInput.checked = true;   // mark for deletion
                    row.style.display = 'none';   // hide only
                }

                updateTotal();
            });
        }
    }

  
   

    // Add new row dynamically
    document.getElementById('add-row').addEventListener('click', function () {

        const totalForms = document.querySelector('[name$="-TOTAL_FORMS"]');
        const formIdx = parseInt(totalForms.value);

        const emptyRow = document.querySelector('#empty-form-row').cloneNode(true);

        emptyRow.removeAttribute('id');
        emptyRow.style.display = '';

        // Replace __prefix__ with correct index
        emptyRow.innerHTML = emptyRow.innerHTML.replace(/__prefix__/g, formIdx);

        document.querySelector('#items-table tbody').appendChild(emptyRow);

        totalForms.value = formIdx + 1;

        bindRowEvents(emptyRow, priceMap);
    });

    
    document.querySelectorAll('.product-select').forEach(function(select) {
        Array.from(select.options).forEach(option => {
            const productId = option.value;
            if (priceMap[productId]) {
                option.setAttribute('data-price', priceMap[productId]);
            }
        });
    });

    // document.addEventListener('change', function(e) {
    //     if (e.target.classList.contains('product-select')) {

    //         const select = e.target;
    //         const selectedOption = select.options[select.selectedIndex];
    //         const price = selectedOption.getAttribute('data-price');

    //         const row = select.closest('tr');
    //         const priceInput = row.querySelector('.price-input');
    //         const hiddenPrice = row.querySelector('input[name$="-price"]');

    //         if (price) {
    //             priceInput.value = price;
    //             hiddenPrice.value = price;
    //         }
    //     }
    // });

        
    const table = document.querySelector('#items-table');
    if (!table) return;
    const getPriceUrl = table.dataset.getPriceUrl;  // this is /portal/get-product-price/
        
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('product-select')) {

            const select = e.target;
            const productId = select.value;

            if (!productId) return;

            fetch(`${getPriceUrl}?product_id=${productId}`)
                .then(response => response.json())
                .then(data => {

                    const row = select.closest('tr');
                    if (!row) return;

                    const priceInput = row.querySelector('.price-input');
                    const hiddenPrice = row.querySelector('input[name$="-price"]');

                    if (priceInput && hiddenPrice) {
                        priceInput.value = data.price;
                        hiddenPrice.value = data.price;
                    }
                });
        }
    });

});