import React, { useEffect, useState, useContext } from "react";
import { AuthProvider, AuthContext } from "./AuthContext";
import Login from "./Login";
import Logout from "./Logout";
import Signup from "./Signup";
const API_URL = "http://localhost:8080";
const API_KEY = "changeme123";

function App() {
  const { auth, setAuth } = useContext(AuthContext);

  const [showSignup, setShowSignup] = useState(false);
  const [stores, setStores] = useState([]);
  const [selectedStoreId, setSelectedStoreId] = useState("");
  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [cart, setCart] = useState([]);
  const [customer, setCustomer] = useState({ id: "", name: "", contact: "", address: "", payment_method: "" });
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  // Fetch stores on mount
  useEffect(() => {
    fetch(`${API_URL}/stores`, { headers: { "x-api-key": API_KEY } })
      .then(res => !res.ok ? Promise.reject("Failed to fetch stores") : res.json())
      .then(setStores)
      .catch(e => setError(e.message));
  }, []);

  // Fetch products and inventory when store changes
  useEffect(() => {
    if (selectedStoreId) {
      fetch(`${API_URL}/products`, { headers: { "x-api-key": API_KEY } })
        .then(res => !res.ok ? Promise.reject("Failed to fetch products") : res.json())
        .then(setProducts)
        .catch(e => setError(e.message));
      fetch(`${API_URL}/inventory?store_id=${selectedStoreId}`, { headers: { "x-api-key": API_KEY } })
        .then(res => !res.ok ? Promise.reject("Failed to fetch inventory") : res.json())
        .then(setInventory)
        .catch(e => setError(e.message));
         if (cart.length > 0) {
        setCart([]); // Clear cart on store change
        alert("Cart cleared: Please select products from the new store.");
      }
      setSelectedId("");
      setSelectedProduct(null);
      setQuantity(1);      
    }
  }, [selectedStoreId]);

  useEffect(() => updateSelectedProduct(), [selectedId, products]);
  useEffect(() => updateCustomerFromAuth(), [auth]);

  const updateSelectedProduct = () => {
    const prod = products.find(p => [p._id, p.id, String(p._id), String(p.id)].includes(selectedId));
    setSelectedProduct(prod || null);
    setQuantity(1);
  };

  const updateCustomerFromAuth = () => {
    if (!auth?.user) return;
    setCustomer(prev => ({
      ...prev,
      id: String(auth.user.id || auth.user.username || auth.user.email || ""),
      name: String(auth.user.username || auth.user.name || auth.user.email || "")
    }));
  };

  // Only show products that are in inventory for the selected store and have quantity > 0
  const availableProductIds = new Set(inventory.filter(item => item.quantity > 0).map(item => item.product_id));
  const filteredProducts = products.filter(product => availableProductIds.has(product._id || product.id));

  const handleStoreChange = e => {
    setSelectedStoreId(e.target.value);
    // Cart and product selection are cleared in the useEffect above
  };

  const handleAddToCart = () => {
    if (!selectedProduct) return;
    setCart(prev => [...prev, {
      product_id: selectedProduct._id || selectedProduct.id,
      name: selectedProduct.name,
      price: selectedProduct.price,
      quantity
    }]);
    resetSelection();
  };

  const resetSelection = () => {
    setSelectedId("");
    setSelectedProduct(null);
    setQuantity(1);
  };

  const handleRemoveFromCart = idx => setCart(prev => prev.filter((_, i) => i !== idx));
  const handleQuantityChange = (idx, qty) => setCart(prev => prev.map((item, i) => i === idx ? { ...item, quantity: qty } : item));
  const handleCustomerChange = e => setCustomer({ ...customer, [e.target.name]: e.target.value });
  const isCustomerValid = () =>
    String(customer.id).trim() &&
    String(customer.name).trim() &&
    customer.contact.trim() &&
    customer.address.trim() &&
    customer.payment_method.trim();
  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const placeOrder = async () => {
    setResult(""); setError("");
    if (!cart.length) return setError("Cart is empty");
    if (!isCustomerValid()) return setError("Please fill all customer details");
    if (!selectedStoreId) return setError("Please select a store.");
    try {
      const response = await fetch(`${API_URL}/orders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": API_KEY,
          "Authorization": `Bearer ${auth.token}`
        },
        body: JSON.stringify({
          customer_id: String(customer.id),
          customer_name: String(customer.name),
          customer_contact: customer.contact,
          delivery_address: customer.address,
          amount: totalAmount,
          payment_method: customer.payment_method,
          store_id: parseInt(selectedStoreId),
          items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity,
            price: item.price
          }))
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || JSON.stringify(data));
      setResult(`Order placed! ID: ${data.id || JSON.stringify(data)}`);
      setCart([]);
    } catch (e) {
      setError(e.message);
    }
  };

  if (!auth) return (
    <div style={{ maxWidth: 400, margin: "0 auto" }}>
      {showSignup ?
        (<><Signup /><button onClick={() => setShowSignup(false)}>Login</button></>) :
        (<><Login /><button onClick={() => setShowSignup(true)}>Sign up</button></>)
      }
    </div>
  );

  return (
    <div style={{ maxWidth: 600, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Place Order</h2>
      <div>
        <span>Welcome, {auth?.user?.username || auth?.user?.email || "User"}</span>
        <Logout />
      </div>
      </div>
      <div>
        <label>
          Store:
          <select value={selectedStoreId} onChange={handleStoreChange}>
            <option value="">Select store</option>
            {stores.map(store => (
              <option key={store.id || store._id} value={store.id || store._id}>{store.name}</option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <label>Product:
          <select value={selectedId} onChange={e => setSelectedId(e.target.value)} disabled={!selectedStoreId}>
            <option value="">Select product</option>
            {filteredProducts.map(p => <option key={p._id || p.id} value={p._id || p.id}>{p.name}</option>)}
          </select>
        </label>
        {selectedProduct && (
          <div>
            <div>Name: {selectedProduct.name}</div>
            <div>Price: {selectedProduct.price}</div>
            <input type="number" min="1" value={quantity} onChange={e => setQuantity(Number(e.target.value))} />
            <button onClick={handleAddToCart}>Add to Cart</button>
          </div>
        )}
      </div>
      <h3>Cart</h3>
      {cart.map((item, idx) => (
        <div key={idx}>
          {item.name} - Qty:
          <input type="number" min="1" value={item.quantity}
            onChange={e => handleQuantityChange(idx, Number(e.target.value))} />
          <button onClick={() => handleRemoveFromCart(idx)}>Remove</button>
        </div>
      ))}
      <h3>Customer Details</h3>
      <div><strong>Name:</strong> {customer.name}</div>
      <div>
        <label htmlFor="contact-input">Contact:&nbsp;
          <input
            id="contact-input"
            name="contact"
            value={customer.contact}
            onChange={handleCustomerChange}
            placeholder="Contact"
            style={{ marginLeft: 8 }}
          />
        </label>
      </div>
      <div>
        <label htmlFor="address-input">Address:&nbsp;
          <input
            id="address-input"
            name="address"
            value={customer.address}
            onChange={handleCustomerChange}
            placeholder="Address"
            style={{ marginLeft: 8 }}
          />
        </label>
      </div>
      <div>
        <label htmlFor="payment-method-input">Payment Method:&nbsp;
          <select
            id="payment-method-input"
            name="payment_method"
            value={customer.payment_method}
            onChange={handleCustomerChange}
            style={{ marginLeft: 8 }}
          >
            <option value="">Select</option>
            <option value="credit_card">Credit Card</option>
            <option value="debit_card">Debit Card</option>
            <option value="cash">Cash</option>
            <option value="upi">UPI</option>
          </select>
        </label>
      </div>
      <div><strong>Total: {totalAmount.toFixed(2)}</strong></div>
      <button onClick={placeOrder} disabled={!cart.length}>Place Order</button>
      {result && <div style={{ color: "green" }}>{result}</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
}

export default function WrappedApp() {
  return <AuthProvider><App /></AuthProvider>;
}
