document.addEventListener('DOMContentLoaded', function() {
    const tbodyList = document.querySelectorAll('.table tbody');

    tbodyList.forEach(tbody => {
        tbody.addEventListener('click', function(event) {
            const row = event.target.closest('tr');
            if (!row) return;

            // Ignore clicks on buttons or links
            if (event.target.closest('button, a')) return;

            tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
            row.classList.add('selected');
        });
    });

    // Auto-select row after edit
    const urlParams = new URLSearchParams(window.location.search);
    const selectedId = urlParams.get('selected');
    if (selectedId) {
        const row = document.querySelector(`tr[data-menu-id="${selectedId}"]`);
        if (row) row.classList.add('selected');
    }

    // Dropdown submenu toggle
    document.querySelectorAll('.dropdown-submenu > a').forEach(function(el) {
        el.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.parentElement.classList.toggle('show');
        });
    });

    // Auto logout
    const logoutTimeout = 10 * 60 * 1000;
    let logoutTimer;
    function logoutUser() {
        if (typeof logoutUrl !== "undefined") {
            window.location.href = logoutUrl;
        }
    }
    function resetTimer() {
        clearTimeout(logoutTimer);
        logoutTimer = setTimeout(logoutUser, logoutTimeout);
    }
    ['load', 'mousemove', 'click', 'scroll', 'keydown'].forEach(evt =>
        window.addEventListener(evt, resetTimer)
    );
});



// document.addEventListener("DOMContentLoaded", function () {

//     function calculateTotals() {
//         let total = 0;

//         document.querySelectorAll("#items-table tbody tr").forEach(row => {
//             const qty = parseFloat(row.querySelector("[name$='quantity']")?.value) || 0;
//             const price = parseFloat(row.querySelector("[name$='price']")?.value) || 0;

//             const subtotal = qty * price;
//             row.querySelector(".subtotal").innerText = subtotal.toFixed(2);

//             total += subtotal;
//         });

//         document.getElementById("total-amount").innerText = total.toFixed(2);
//     }

//     document.addEventListener("input", calculateTotals);

//     // Remove row
//     document.addEventListener("click", function(e){
//         if(e.target.classList.contains("remove-row")){
//             e.target.closest("tr").remove();
//             calculateTotals();
//         }
//     });

//     calculateTotals();
// });