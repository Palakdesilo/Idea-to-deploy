"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { ShoppingCart, User, Search, X } from 'lucide-react'; // Using Lucide React Icons

// Mock API utility - In a real application, this would be imported from '@/lib/api'
// and handle actual HTTP requests, authentication, etc.
const api = {
  get: async (path: string) => {
    console.log(`Mock API GET: ${path}`);
    // Simulate network delay
    return new Promise(resolve => setTimeout(() => resolve({ data: [] }), 500));
  },
  post: async (path: string, data: any) => {
    console.log(`Mock API POST: ${path}`, data);
    // Simulate network delay
    return new Promise(resolve => setTimeout(() => resolve({ success: true }), 500));
  },
};

// Design Tokens
const primaryColor = '#0f172a'; // Corresponds to slate-900 in Tailwind
const secondaryColor = '#3b82f6'; // Corresponds to blue-500 in Tailwind
const borderRadius = '1rem'; // Corresponds to rounded-xl in Tailwind

// Define the structure for a cart item
interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  imageUrl: string;
}

export default function ShoppingCartPage() {
  const router = useRouter();

  // Mock cart items state
  const [cartItems, setCartItems] = useState<CartItem[]>([
    { id: '1', name: 'Premium Wireless Headphones', price: 100.00, quantity: 1, imageUrl: '/placeholder-product.jpg' },
    { id: '2', name: 'Ergonomic Office Chair', price: 50.00, quantity: 2, imageUrl: '/placeholder-product.jpg' },
    { id: '3', name: 'Smart Home Assistant', price: 20.00, quantity: 1, imageUrl: '/placeholder-product.jpg' },
  ]);

  const [discountCode, setDiscountCode] = useState('');
  const [isUpdatingCart, setIsUpdatingCart] = useState(false);
  const [isApplyingDiscount, setIsApplyingDiscount] = useState(false);

  // Function to update the quantity of a specific item in the cart
  const updateQuantity = (id: string, newQuantity: number) => {
    setCartItems(prevItems =>
      prevItems.map(item =>
        item.id === id ? { ...item, quantity: Math.max(1, newQuantity) } : item
      )
    );
  };

  // Function to remove an item from the cart
  const removeItem = (id: string) => {
    setCartItems(prevItems => prevItems.filter(item => item.id !== id));
  };

  // Function to calculate the subtotal of all items in the cart
  const calculateSubtotal = () => {
    return cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  // Handler for the "Update Cart" button, simulating an API call
  const handleUpdateCart = async () => {
    setIsUpdatingCart(true);
    try {
      // In a real app, this would send the updated cart to the backend
      await api.post('/api/cart/update', { items: cartItems });
      alert('Cart updated successfully!');
    } catch (error) {
      console.error('Failed to update cart:', error);
      alert('Failed to update cart.');
    } finally {
      setIsUpdatingCart(false);
    }
  };

  // Handler for the "Apply Discount" button, simulating an API call
  const handleApplyDiscount = async () => {
    setIsApplyingDiscount(true);
    try {
      // In a real app, this would validate and apply the discount code
      await api.post('/api/discount/apply', { code: discountCode, cartSubtotal: calculateSubtotal() });
      alert(`Discount code "${discountCode}" applied! (Simulated)`);
      // A real application would update the cart totals based on the API response here
    } catch (error) {
      console.error('Failed to apply discount:', error);
      alert('Failed to apply discount.');
    } finally {
      setIsApplyingDiscount(false);
    }
  };

  // The total for the order summary (simplified to subtotal for this page)
  const total = calculateSubtotal();

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      {/* Header Section */}
      <header
        className="w-full bg-white shadow-sm py-4 px-6 flex items-center justify-between sticky top-0 z-10"
        style={{ height: '80px' }}
      >
        <Link href="/homepage" className="text-2xl font-bold text-gray-900">
          Logo
        </Link>
        <nav className="flex space-x-8 text-lg font-medium">
          <Link href="/product-listing-page" className="hover:text-blue-600 transition-colors duration-300">Shop</Link>
          <Link href="/category-page" className="hover:text-blue-600 transition-colors duration-300">Categories</Link>
          <Link href="#" className="hover:text-blue-600 transition-colors duration-300">Deals</Link>
          <Link href="#" className="hover:text-blue-600 transition-colors duration-300">About Us</Link>
        </nav>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
              style={{ width: '250px', height: '32px' }}
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          </div>
          <Link href="/login-/-register-page" className="p-2 rounded-md hover:bg-gray-100 transition-colors duration-300">
            <User size={20} />
          </Link>
          <Link href="/shopping-cart-page" className="relative p-2 rounded-md hover:bg-gray-100 transition-colors duration-300">
            <ShoppingCart size={20} />
            {cartItems.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                {cartItems.length}
              </span>
            )}
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow container mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-8" style={{ paddingTop: '96px' }}>
        {/* Left Column: Shopping Cart Details */}
        <section className="lg:col-span-2 bg-white p-8 shadow-lg" style={{ borderRadius: borderRadius }}>
          <h1 className="text-3xl font-bold mb-8 text-gray-900">Shopping Cart</h1>

          {cartItems.length === 0 ? (
            <div className="text-center py-16 text-gray-500 text-xl">Your cart is empty.</div>
          ) : (
            <>
              {/* Cart Header Row */}
              <div className="grid grid-cols-6 gap-4 pb-4 border-b border-gray-200 text-gray-500 font-semibold text-sm">
                <div className="col-span-2">Product</div>
                <div>Price</div>
                <div>Quantity</div>
                <div>Subtotal</div>
                <div></div> {/* Placeholder for remove button column */}
              </div>

              {/* Individual Cart Items */}
              {cartItems.map((item) => (
                <div key={item.id} className="grid grid-cols-6 gap-4 py-6 border-b border-gray-100 items-center">
                  <div className="col-span-2 flex items-center space-x-4">
                    <Image
                      src={item.imageUrl}
                      alt={item.name}
                      width={64}
                      height={64}
                      className="rounded-md object-cover border border-gray-200"
                    />
                    <span className="font-medium text-gray-900">{item.name}</span>
                  </div>
                  <div className="text-gray-700">${item.price.toFixed(2)}</div>
                  <div>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => updateQuantity(item.id, parseInt(e.target.value))}
                      className="w-20 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-400 transition-all duration-300"
                      style={{ height: '24px' }}
                    />
                  </div>
                  <div className="font-semibold text-gray-900">${(item.price * item.quantity).toFixed(2)}</div>
                  <div>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-red-500 hover:text-red-700 transition-colors duration-300 p-1 rounded-md hover:bg-red-50"
                      aria-label={`Remove ${item.name}`}
                    >
                      <X size={18} />
                    </button>
                  </div>
                </div>
              ))}

              {/* Cart Action Buttons */}
              <div className="flex justify-between mt-8 space-x-4">
                <Link
                  href="/product-listing-page"
                  className="px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-md hover:bg-gray-300 transition-all duration-300"
                  style={{ borderRadius: borderRadius }}
                >
                  Continue Shopping
                </Link>
                <button
                  onClick={handleUpdateCart}
                  disabled={isUpdatingCart}
                  className="px-6 py-3 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{ backgroundColor: secondaryColor, borderRadius: borderRadius }}
                >
                  {isUpdatingCart ? 'Updating...' : 'Update Cart'}
                </button>
              </div>
            </>
          )}
        </section>

        {/* Right Column: Order Summary */}
        <section className="lg:col-span-1 bg-white p-8 shadow-lg" style={{ borderRadius: borderRadius }}>
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Order Summary</h2>

          <div className="space-y-4 mb-6">
            <div className="flex justify-between text-lg">
              <span>Subtotal:</span>
              <span className="font-semibold">${calculateSubtotal().toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>Shipping:</span>
              <span>Calculated at Checkout</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>Tax:</span>
              <span>Calculated at Checkout</span>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-6 mb-6">
            <div className="flex items-center space-x-2 mb-4">
              <input
                type="text"
                placeholder="Discount Code"
                value={discountCode}
                onChange={(e) => setDiscountCode(e.target.value)}
                className="flex-grow p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-400 transition-all duration-300"
                style={{ height: '32px' }}
              />
              <button
                onClick={handleApplyDiscount}
                disabled={isApplyingDiscount || !discountCode.trim()}
                className="px-4 py-2 bg-gray-700 text-white font-semibold rounded-md hover:bg-gray-800 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ backgroundColor: primaryColor, borderRadius: borderRadius, height: '32px' }}
              >
                {isApplyingDiscount ? 'Applying...' : 'Apply'}
              </button>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-6 mb-8">
            <div className="flex justify-between items-center text-2xl font-bold text-gray-900">
              <span>TOTAL:</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>

          <Link
            href="/checkout-page"
            className="w-full flex justify-center items-center px-6 py-4 bg-blue-600 text-white text-xl font-bold rounded-md hover:bg-blue-700 transition-all duration-300"
            style={{ backgroundColor: secondaryColor, borderRadius: borderRadius, height: '48px' }}
          >
            PROCEED TO CHECKOUT
          </Link>
        </section>
      </main>

      {/* Footer Section */}
      <footer
        className="w-full bg-gray-900 text-white py-6 px-6 mt-auto"
        style={{ height: '100px', backgroundColor: primaryColor }}
      >
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between text-sm">
          <p className="mb-4 md:mb-0">&copy; 2023 E-commerce Site</p>
          <nav className="flex space-x-6 mb-4 md:mb-0">
            <Link href="#" className="hover:text-blue-400 transition-colors duration-300">About Us</Link>
            <Link href="#" className="hover:text-blue-400 transition-colors duration-300">Contact</Link>
            <Link href="#" className="hover:text-blue-400 transition-colors duration-300">FAQ</Link>
            <Link href="#" className="hover:text-blue-400 transition-colors duration-300">Privacy</Link>
          </nav>
          <div className="flex items-center space-x-4">
            <span className="mr-2">Social Icons</span> {/* Placeholder for actual social icons */}
            <input
              type="email"
              placeholder="Email for Newsletter"
              className="p-2 border border-gray-700 bg-gray-800 text-white rounded-md focus:outline-none focus:ring-1 focus:ring-blue-400 transition-all duration-300"
              style={{ width: '200px', height: '24px' }}
            />
            <button
              className="px-4 py-2 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600 transition-all duration-300"
              style={{ backgroundColor: secondaryColor, borderRadius: borderRadius, height: '24px' }}
            >
              Subscribe
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}