import { useState } from 'react';

function EggOrder() {
  const [customerName, setCustomerName] = useState('');
  const [numCrates, setNumCrates] = useState(0);
  const [price, setPrice] = useState(0);
  const [dueTime, setDueTime] = useState('');
  const [orders, setOrders] = useState([]);

  const fetchOrders = async () => {
    const response = await fetch('http://127.0.0.1:5000/orders');
    const data = await response.json();
    setOrders(data);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const order = { customer_name: customerName, num_crates: numCrates, price, due_time: dueTime };
    await fetch('http://127.0.0.1:5000/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(order),
    });
    fetchOrders();
  };

  const handleDelete = async (id) => {
    await fetch(`http://127.0.0.1:5000/orders/${id}`, { method: 'DELETE' });
    fetchOrders();
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Customer Name:
          <input type="text" value={customerName} onChange={(event) => setCustomerName(event.target.value)} />
        </label>
        <br />
        <label>
          Number of Crates:
          <input type="number" value={numCrates} onChange={(event) => setNumCrates(event.target.value)} />
        </label>
        <br />
        <label>
          Price:
          <input type="number" value={price} onChange={(event) => setPrice(event.target.value)} />
        </label>
        <br />
        <label>
          Due Time:
          <input type="datetime-local" value={dueTime} onChange={(event) => setDueTime(event.target.value)} />
        </label>
        <br />
        <button type="submit">Submit Order</button>
      </form>
      <h2>Orders</h2>
      <button onClick={fetchOrders}>Refresh Orders</button>
      <ul>
        {orders.map((order) => (
          <li key={order[0]}>
            {`ID: ${order[0]}, Customer: ${order[1]}, Crates: ${order[2]}, Price: ${order[3]}, Due Time: ${order[4]}`}
            <button onClick={() => handleDelete(order[0])}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default EggOrder;