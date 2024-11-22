document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const responseMessage = document.getElementById('response-message');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const response = await fetch(uploadForm.action, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            responseMessage.textContent = result.message;
        });
    }

    // Fetch and display portfolio data
    async function fetchPortfolio() {
        const response = await fetch('/get-portfolio');
        const portfolio = await response.json();
        const portfolioTableBody = document.querySelector('#portfolio-table tbody');
        
        portfolio.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.symbol}</td>
                <td>${item.quantity}</td>
                <td>${item.buyPrice}</td>
                <td>${item.currentPrice}</td>
            `;
            portfolioTableBody.appendChild(row);
        });
    }

    fetchPortfolio();
});

document.addEventListener('DOMContentLoaded', () => {
    const addStockBtn = document.getElementById('add-stock-btn');
    const updateStockBtn = document.getElementById('update-stock-btn');
    const deleteStockBtn = document.getElementById('delete-stock-btn');

    // Handle Add New Stock Button
    addStockBtn.addEventListener('click', () => {
        // You can implement a form here or redirect to another page for adding a stock
        alert('Redirecting to add stock form (or show form here).');
    });

    // Handle Update Stock Button (Example of Modal or Redirection)
    updateStockBtn.addEventListener('click', () => {
        const stockId = prompt('Enter the stock ID to update:');
        if (stockId) {
            window.location.href = `/update-stock/${stockId}`;
        }
    });

    // Handle Delete Stock Button (Example of Modal or Redirection)
    deleteStockBtn.addEventListener('click', () => {
        const stockId = prompt('Enter the stock ID to delete:');
        if (stockId) {
            window.location.href = `/delete-stock/${stockId}`;
        }
    });

    // Handle Edit and Delete buttons in the table
    const editBtns = document.querySelectorAll('.edit-btn');
    const deleteBtns = document.querySelectorAll('.delete-btn');

    editBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const stockId = e.target.getAttribute('data-id');
            window.location.href = `/update-stock/${stockId}`;
        });
    });

    deleteBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const stockId = e.target.getAttribute('data-id');
            const confirmDelete = confirm('Are you sure you want to delete this stock?');
            if (confirmDelete) {
                window.location.href = `/delete-stock/${stockId}`;
            }
        });
    });
});

document.getElementById('delete-all-btn').addEventListener('click', function() {
    const confirmDelete = confirm('Are you sure you want to delete all stocks in your portfolio? This action cannot be undone.');
    
    if (confirmDelete) {
        // Redirect to delete-all route
        window.location.href = '/delete-all';  // Trigger the deletion route
    }
});
function formatIndianNumber(num) {
    // Convert to string and reverse it for easier formatting
    var num_str = num.toString().split('').reverse().join('');
    
    // Add commas after every 2 digits, except the first group
    var formatted = num_str.replace(/(\d{3})(?=\d)/g, '$1,');
    
    // Reverse the formatted string back
    return formatted.split('').reverse().join('');
}

// Format the numeric fields on page load
window.onload = function() {
    // Format Total Invested and Current Value
    var totalInvested = document.getElementById("total-invested");
    var totalCurrentValue = document.getElementById("total-current-value");

    if (totalInvested) {
        totalInvested.innerText = formatIndianNumber(totalInvested.innerText);
    }

    if (totalCurrentValue) {
        totalCurrentValue.innerText = formatIndianNumber(totalCurrentValue.innerText);
    }

    // Format individual stock prices (if needed)
    var stockPrices = document.querySelectorAll(".stock-price");
    stockPrices.forEach(function(element) {
        element.innerText = formatIndianNumber(element.innerText);
    });
};