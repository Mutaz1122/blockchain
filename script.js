const balanceDisplay = document.getElementById('balance-display');

async function getBalance() {
  const senderAddress = prompt('Enter your address:');
  if (!senderAddress) return;

  try {
    const response = await fetch('localhost:5000/balance', {
      method: 'POST',
      body: JSON.stringify({ sender: senderAddress }),
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const balance = await response.json();
    balanceDisplay.value = balance;
  } catch (error) {
    console.error(error);
    alert('Error getting balance');
  }
}

async function mineBlock() {

  try {
    const response = await fetch('http://localhost:5000/mine', {
      method: 'GET',
      mode: 'no-cors'
    
    });

    setTimeout(async () => {
        // Your code to run after 1 second
      
      }, 1000); 
      const data = await response.text();
        alert(data);
    // if (data.message === 'New Block Mined') {
    //   alert('Block mined successfully!');
    //   updateBlockchainUI(); // Update balance and transactions after mining
    // } else {
    //   alert('Failed to mine block. Please try again later.');
    // }
  } catch (error) {
    console.error(error);
    alert(error);
  }
}

const transactionForm = document.getElementById('transaction-form');

transactionForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const recipientAddress = document.getElementById('recipient-address').value;
  const transactionAmount = document.getElementById('transaction-amount').value;

  try {
    const response = await fetch('localhost:5000/transactions/new', {
      method: 'POST',
      body: JSON.stringify({ recipient: recipientAddress, amount: transactionAmount }),
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    if (data.message === 'Transaction successful') {
      alert('Transaction sent successfully!');
      updateBlockchainUI(); // Update balance and transactions after sending transaction
      transactionForm.reset(); // Clear transaction form after successful submission
    } else {
      alert('Error sending transaction: ' + data.error);
    }
  } catch (error) {
    console.error(error);
    alert('Error sending transaction');
  }
});

// Add function to update UI elements
async function updateBlockchainUI() {
  // Fetch updated balance
  await getBalance();

  // Fetch recent transactions (optional)
  // ...

  // Update UI elements based on fetched data
  // ...
}

// Add additional functionalities based on backend capabilities

// ...
