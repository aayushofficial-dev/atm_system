document.addEventListener('DOMContentLoaded', function() {
  const depositForm = document.getElementById('deposit-form');
  const withdrawForm = document.getElementById('withdraw-form');
  const balanceEl = document.getElementById('balance');
  const messages = document.getElementById('messages');
  const txList = document.getElementById('tx-list');

  function showMessage(text, type='info'){
    messages.innerHTML = `<div class="alert alert-${type} py-1">${text}</div>`;
    setTimeout(()=> messages.innerHTML = '', 4000);
  }

  if(depositForm){
    depositForm.addEventListener('submit', async function(e){
      e.preventDefault();
      const amount = parseFloat(document.getElementById('deposit-amount').value);
      const res = await fetch('/deposit', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({amount})
      });
      const data = await res.json();
      if(data.success){
        balanceEl.textContent = data.balance;
        showMessage(data.message, 'success');
        // reload transactions
        loadTransactions();
      } else {
        showMessage(data.message || 'Error', 'warning');
      }
    });
  }

  if(withdrawForm){
    withdrawForm.addEventListener('submit', async function(e){
      e.preventDefault();
      const amount = parseFloat(document.getElementById('withdraw-amount').value);
      const res = await fetch('/withdraw', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({amount})
      });
      const data = await res.json();
      if(data.success){
        balanceEl.textContent = data.balance;
        showMessage(data.message, 'success');
        loadTransactions();
      } else {
        showMessage(data.message || 'Error', 'warning');
      }
    });
  }

  async function loadTransactions(){
    const res = await fetch('/api/transactions');
    if(!res.ok) return;
    const data = await res.json();
    if(data.success){
      txList.innerHTML = '';
      if(data.transactions.length === 0){
        txList.innerHTML = '<li class="list-group-item">No transactions yet.</li>';
      } else {
        data.transactions.slice(-20).reverse().forEach(t => {
          const li = document.createElement('li');
          li.className = 'list-group-item';
          li.textContent = t;
          txList.appendChild(li);
        });
      }
    }
  }

  // initial load
  loadTransactions();
});
