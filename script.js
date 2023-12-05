const balanceDisplay = document.getElementById('balance-display');


async function address() {
  x = document.getElementById("nodeAddress").value;
  try {
    const response = await fetch(`http://127.0.0.1:${x}/blockchain`, {
      method: 'GET',
      mode: 'no-cors'
    });
    localStorage.setItem("address", x);
    window.location.replace("HomePage.html");
  }
  catch (e){
    alert(e)
  }
}

async function loadPage(){
  document.getElementById("nodeNumber").innerHTML = localStorage.getItem("address");
  try{
  const responseAddress = await fetch(`http://127.0.0.1:${localStorage.getItem("address")}/mine`, {
      method: 'GET',
      mode: 'cors'
    
    });
    const data = await responseAddress.json();
    localStorage.setItem("senderAddress",data["transactions"][0]["recipient"]);
  }
    catch (error) {
      console.error(error);
      alert('Error getting address');
    }
}

async function getBalance() {

  senderAddress = localStorage.getItem("senderAddress");
  if (!senderAddress) return;
  try {
    const response = await fetch(`http://127.0.0.1:${localStorage.getItem("address")}/balance`, {
      method: 'POST',
      body: JSON.stringify({ sender: senderAddress }),
      headers: {
        'Content-Type': 'application/json',
        mode: 'cors',
        "Access-Control-Allow-Origin": `*`

      }
    });

    const balance = await response.json();
    document.getElementById("balanceDisplay").innerHTML = balance;
  } catch (error) {
    console.error(error);
    alert('Error getting balance');
  }
}

async function mineBlock() {

  try {
    const response = await fetch(`http://127.0.0.1:${localStorage.getItem("address")}/mine`, {
      method: 'GET',
      mode: 'cors'
    
    });

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
