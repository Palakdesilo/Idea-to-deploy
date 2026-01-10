"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Search, User, ShoppingCart, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

// Design Tokens
const primaryColor = '#0f172a'; // slate-900
const secondaryColor = '#3b82f6'; // blue-500
const borderRadius = '1rem'; // rounded-xl

// Mock Data for demonstration
const categories = [
  { name: 'Electronics', href: '/category-page?category=electronics' },
  { name: 'Apparel', href: '/category-page?category=apparel' },
  { name: 'Home Goods', href: '/category-page?category=home-goods' },
  { name: 'Books', href: '/category-page?category=books' },
  { name: 'Sports & Outdoors', href: '/category-page?category=sports-outdoors' },
];

const brands = [
  { name: 'Fashionista', checked: true },
  { name: 'UrbanWear', checked: false },
  { name: 'SportFit', checked: false },
  { name: 'EcoChic', checked: false },
];

const colors = [
  { name: 'Red', hex: '#ef4444', checked: false },
  { name: 'Blue', hex: '#3b82f6', checked: true },
  { name: 'Green', hex: '#22c55e', checked: false },
  { name: 'Black', hex: '#000000', checked: false },
  { name: 'White', hex: '#ffffff', checked: false },
];

const sizes = [
  { name: 'XS', checked: false },
  { name: 'S', checked: true },
  { name: 'M', checked: false },
  { name: 'L', checked: false },
  { name: 'XL', checked: false },
];

const products = [
  {
    id: '1',
    name: 'Elegant Summer Dress',
    price: 49.99,
    imageUrl: 'https://via.placeholder.com/150/fca5a5/fee2e2?text=Dress',
    href: '/product-detail-page?id=1',
  },
  {
    id: '2',
    name: 'Stylish Denim Jacket',
    price: 79.99,
    imageUrl: 'https://via.placeholder.com/150/93c5fd/eff6ff?text=Jacket',
    href: '/product-detail-page?id=2',
  },
  {
    id: '3',
    name: 'Comfortable Running Shoes',
    price: 89.99,
    imageUrl: 'https://via.placeholder.com/150/a78bfa/ede9fe?text=Shoes',
    href: '/product-detail-page?id=3',
  },
  {
    id: '4',
    name: 'Classic Leather Handbag',
    price: 129.99,
    imageUrl: 'https://via.placeholder.com/150/fcd34d/fffbeb?text=Handbag',
    href: '/product-detail-page?id=4',
  },
  {
    id: '5',
    name: 'Premium Smartwatch',
    price: 199.99,
    imageUrl: 'https://via.placeholder.com/150/6ee7b7/ecfdf5?text=Watch',
    href: '/product-detail-page?id=5',
  },
  {
    id: '6',
    name: 'Wireless Noise-Cancelling Headphones',
    price: 149.99,
    imageUrl: 'https://via.placeholder.com/150/f0abfc/fdf2f8?text=Headphones',
    href: '/product-detail-page?id=6',
  },
  {
    id: '7',
    name: 'Ergonomic Office Chair',
    price: 249.99,
    imageUrl: 'https://via.placeholder.com/150/cbd5e1/f1f5f9?text=Chair',
    href: '/product-detail-page?id=7',
  },
  {
    id: '8',
    name: 'High-Performance Blender',
    price: 99.99,
    imageUrl: 'https://via.placeholder.com/150/fca5a5/fee2e2?text=Blender',
    href: '/product-detail-page?id=8',
  },
  {
    id: '9',
    name: 'Travel Backpack with Laptop Sleeve',
    price: 69.99,
    imageUrl: 'https://via.placeholder.com/150/93c5fd/eff6ff?text=Backpack',
    href: '/product-detail-page?id=9',
  },
];

const CategoryPage: React.FC = () => {
  const router = useRouter();
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(200); // Example range for price slider

  // In a real application, currentCategory would be derived from URL params
  const currentCategory = "Apparel";

  const handleApplyFilters = () => {
    // This function would typically trigger an API call or update URL parameters
    // to fetch filtered products. For this component, it's a placeholder.
    console.log('Applying filters:', { minPrice, maxPrice, brands, colors, sizes });
    // Example API call (if api client were integrated and actual filtering was implemented):
    // api.get('/api/products', { params: { minPrice, maxPrice, brands, colors, sizes } })
    //   .then(response => setProducts(response.data))
    //   .catch(error => console.error("Error fetching filtered products:", error));
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen flex flex-col bg-gray-50 text-gray-900" // Lighter background for main content
    >
      {/* Header */}
      <header
        className="sticky top-0 z-50 w-full p-4 flex items-center justify-between shadow-md"
        style={{ backgroundColor: primaryColor, color: 'white' }}
      >
        <Link href="/homepage" className="text-2xl font-bold tracking-tight">
          E-Shop
        </Link>
        <nav className="hidden md:flex gap-6">
          <Link href="/homepage" className="hover:text-secondary transition-colors duration-200">Home</Link>
          <Link href="/product-listing-page" className="hover:text-secondary transition-colors duration-200">Shop All</Link>
          <Link href="/category-page" className="hover:text-secondary transition-colors duration-200">Categories</Link>
          <Link href="#" className="hover:text-secondary transition-colors duration-200">Contact</Link>
        </nav>
        <div className="flex items-center gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search products..."
              className="pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-secondary"
              style={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'white', borderRadius: borderRadius }}
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-300" size={18} />
          </div>
          <Link href="/login-/-register-page" className="p-2 hover:text-secondary transition-colors duration-200" aria-label="User Account">
            <User size={20} />
          </Link>
          <Link href="/shopping-cart-page" className="relative p-2 hover:text-secondary transition-colors duration-200" aria-label="Shopping Cart">
            <ShoppingCart size={20} />
            <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">0</span>
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-1 max-w-7xl mx-auto w-full py-8 px-4">
        {/* Sidebar */}
        <aside className="w-64 pr-8 border-r border-gray-200 sticky top-24 self-start">
          {/* Breadcrumbs */}
          <div className="mb-4 text-sm text-gray-600 flex items-center">
            <Link href="/homepage" className="hover:underline">Home</Link>
            <ChevronRight size={12} className="inline-block mx-1" />
            <span className="font-medium">{currentCategory}</span>
          </div>

          {/* Category Title */}
          <h1 className="text-3xl font-bold mb-6" style={{ color: primaryColor }}>
            {currentCategory}
          </h1>

          {/* Category Navigation List */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3" style={{ color: primaryColor }}>Shop by Category</h3>
            <ul className="space-y-2">
              {categories.map((cat) => (
                <li key={cat.name}>
                  <Link
                    href={cat.href}
                    className={`block py-1 px-3 rounded-md transition-all duration-200
                               ${currentCategory === cat.name ? 'bg-secondary text-white' : 'hover:bg-gray-200'}`}
                    style={{ borderRadius: '0.5rem' }} // Slightly smaller radius for list items
                  >
                    {cat.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Filters Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3" style={{ color: primaryColor }}>Filters</h3>

            {/* Price Range Slider */}
            <div className="mb-4">
              <label htmlFor="price-range" className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
              <div className="flex items-center justify-between text-sm mb-2">
                <span>${minPrice}</span>
                <span>${maxPrice}+</span>
              </div>
              <input
                type="range"
                id="price-range"
                min="0"
                max="500"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-secondary"
              />
            </div>

            {/* Brand Checkbox List */}
            <div className="mb-4">
              <h4 className="text-md font-medium text-gray-700 mb-2">Brand</h4>
              {brands.map((brand) => (
                <div key={brand.name} className="flex items-center mb-1">
                  <input
                    type="checkbox"
                    id={`brand-${brand.name}`}
                    name="brand"
                    defaultChecked={brand.checked}
                    className="h-4 w-4 text-secondary rounded focus:ring-secondary border-gray-300"
                  />
                  <label htmlFor={`brand-${brand.name}`} className="ml-2 text-sm text-gray-700">{brand.name}</label>
                </div>
              ))}
            </div>

            {/* Color Swatches/Checkbox List */}
            <div className="mb-4">
              <h4 className="text-md font-medium text-gray-700 mb-2">Color</h4>
              <div className="flex flex-wrap gap-2">
                {colors.map((color) => (
                  <label
                    key={color.name}
                    htmlFor={`color-${color.name}`}
                    className={`relative w-6 h-6 rounded-full cursor-pointer border-2 ${color.checked ? 'border-secondary' : 'border-gray-300'} transition-all duration-200`}
                    style={{ backgroundColor: color.hex }}
                    title={color.name}
                  >
                    <input
                      type="checkbox"
                      id={`color-${color.name}`}
                      name="color"
                      defaultChecked={color.checked}
                      className="sr-only"
                    />
                    {color.checked && (
                      <span className="absolute inset-0 flex items-center justify-center text-white text-xs">✓</span>
                    )}
                  </label>
                ))}
              </div>
            </div>

            {/* Size Checkbox List */}
            <div className="mb-4">
              <h4 className="text-md font-medium text-gray-700 mb-2">Size</h4>
              <div className="flex flex-wrap gap-2">
                {sizes.map((size) => (
                  <label
                    key={size.name}
                    htmlFor={`size-${size.name}`}
                    className={`px-3 py-1 border rounded-md text-sm cursor-pointer transition-all duration-200
                               ${size.checked ? 'bg-secondary text-white border-secondary' : 'border-gray-300 hover:bg-gray-100'}`}
                    style={{ borderRadius: '0.5rem' }}
                  >
                    <input
                      type="checkbox"
                      id={`size-${size.name}`}
                      name="size"
                      defaultChecked={size.checked}
                      className="sr-only"
                    />
                    {size.name}
                  </label>
                ))}
              </div>
            </div>

            {/* Apply Filters Button */}
            <button
              onClick={handleApplyFilters}
              className="w-full py-2 text-white font-semibold transition-all duration-300 hover:opacity-90 shadow-md"
              style={{ backgroundColor: secondaryColor, borderRadius: borderRadius }}
            >
              Apply Filters
            </button>
          </div>
        </aside>

        {/* Product Listing */}
        <main className="flex-1 pl-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <motion.div
                key={product.id}
                className="relative flex flex-col rounded-xl shadow-lg overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
                // Applying glassmorphism effect to product cards
                style={{ backgroundColor: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(10px)', borderRadius: borderRadius }}
                whileHover={{ scale: 1.02 }}
              >
                <Link href={product.href} className="block">
                  <img
                    src={product.imageUrl}
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                </Link>
                <div className="p-4 flex flex-col flex-grow">
                  <Link href={product.href} className="text-lg font-semibold mb-2 hover:text-secondary transition-colors duration-200" style={{ color: primaryColor }}>
                    {product.name}
                  </Link>
                  <p className="text-gray-700 text-xl font-bold mb-4">${product.price.toFixed(2)}</p>
                  <button
                    className="mt-auto py-2 text-white font-semibold transition-all duration-300 hover:opacity-90 shadow-md"
                    style={{ backgroundColor: secondaryColor, borderRadius: borderRadius }}
                    onClick={() => console.log(`Added ${product.name} to cart`)}
                  >
                    Add to Cart
                  </button>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-center mt-12 gap-2">
            {[1, 2, 3].map((page) => (
              <Link
                key={page}
                href={`/category-page?page=${page}`}
                className={`px-4 py-2 rounded-md transition-all duration-200
                           ${page === 1 ? 'bg-secondary text-white shadow-md' : 'bg-gray-200 hover:bg-gray-300'}`}
                style={{ borderRadius: borderRadius }}
              >
                {page}
              </Link>
            ))}
            <span className="px-4 py-2 text-gray-600">...</span>
            <Link
              href="/category-page?page=4"
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-md transition-all duration-200"
              style={{ borderRadius: borderRadius }}
            >
              Next
            </Link>
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer
        className="w-full p-8 text-center text-sm"
        style={{ backgroundColor: primaryColor, color: 'white' }}
      >
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h4 className="font-semibold mb-3">About Us</h4>
            <ul className="space-y-2">
              <li><Link href="#" className="hover:text-secondary transition-colors duration-200">Our Story</Link></li>
              <li><Link href="#" className="hover:text-secondary transition-colors duration-200">Careers</Link></li>
              <li><Link href="#" className="hover:text-secondary transition-colors duration-200">Press</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Customer Service</h4>
            <ul className="space-y-2">
              <li><Link href="#" className="hover:text-secondary transition-colors duration-200">Contact Us</Link></li>
              <li><Link href="#" className="hover:text-secondary transition-colors duration-200">Shipping & Returns</Link></li>
              <li><Link href="#" className="hover:text-secondary transition-colors duration-200">FAQ</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">My Account</h4>
            <ul className="space-y-2">
              <li><Link href="/login-/-register-page" className="hover:text-secondary transition-colors duration-200">Sign In</Link></li>
              <li><Link href="/shopping-cart-page" className="hover:text-secondary transition-colors duration-200">View Cart</Link></li>
              <li><Link href="/checkout-page" className="hover:text-secondary transition-colors duration-200">Checkout</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Follow Us</h4>
            <div className="flex justify-center gap-4 text-xl">
              {/* Placeholder for social icons - In a real app, use actual icons */}
              <Link href="#" className="hover:text-secondary transition-colors duration-200" aria-label="Facebook">FB</Link>
              <Link href="#" className="hover:text-secondary transition-colors duration-200" aria-label="Twitter">TW</Link>
              <Link href="#" className="hover:text-secondary transition-colors duration-200" aria-label="Instagram">IG</Link>
            </div>
            <p className="mt-4">© 2023 E-Shop. All rights reserved.</p>
            <div className="mt-2 text-xs">
              {/* Placeholder for payment method icons - In a real app, use actual icons */}
              Visa, Mastercard, PayPal
            </div>
          </div>
        </div>
      </footer>
    </motion.div>
  );
};

export default CategoryPage;