import React, { useState } from "react";

function App() {
  const [form, setForm] = useState({
    product_id: "",
    quantity: "",
    price: "",
    customer_name: "",
    customer_contact: "",
    delivery_address: "",
  });
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult("");
    setError("");
    // Adjust the URL to your API Gateway or Order Service endpoint
    const url = "http://localhost:8080/orders";
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": "changeme123", // If your API Gateway requires it
        },
        body: JSON.stringify({
          ...form,
          quantity: parseInt(form.quantity, 10),
          price: parseFloat(form.price),
        }),
      });
      if (response.ok) {
        setResult("Order placed successfully!");
        setForm({
          product_id: "",
          quantity: "",
          price: "",
          customer_name: "",
          customer_contact: "",
          delivery_address: "",
        });
      } else {
        const data = await response.json();
        setError(data.error?.message || "Failed to place order");
      }
    } catch (err) {
      setError("Network error: " + err.message);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "2em auto", fontFamily: "Arial" }}>
      <h2>Place an Order</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Product ID:
          <input
            name="product_id"
            value={form.product_id}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <label>
          Quantity:
          <input
            name="quantity"
            type="number"
            value={form.quantity}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <label>
          Price:
          <input
            name="price"
            type="number"
            step="0.01"
            value={form.price}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <label>
          Customer Name:
          <input
            name="customer_name"
            value={form.customer_name}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <label>
          Customer Contact:
          <input
            name="customer_contact"
            value={form.customer_contact}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <label>
          Delivery Address:
          <textarea
            name="delivery_address"
            value={form.delivery_address}
            onChange={handleChange}
            required
          />
        </label>
        <br />
        <button type="submit">Place Order</button>
      </form>
      {result && <div style={{ color: "green", marginTop: "1em" }}>{result}</div>}
      {error && <div style={{ color: "red", marginTop: "1em" }}>{error}</div>}
    </div>
  );
}

export default App;
