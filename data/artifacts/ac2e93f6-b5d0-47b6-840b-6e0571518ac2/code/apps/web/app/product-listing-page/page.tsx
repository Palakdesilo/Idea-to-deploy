"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Search, User, ShoppingCart, ChevronDown, Star } from 'lucide-react';

// Design Tokens
const primaryColor = '#0f172a'; // Tailwind's slate-900
const secondaryColor = '#3b82f6'; // Tailwind's blue-500
const borderRadius = '1rem'; // rounded-xl

// Mock Product Data Interface
interface Product {
  id: string;
  name: string;
  price: number;
  imageUrl: string;
  rating: number;
  reviews: number;
}

// Mock Product Data
const mockProducts: Product[] = [
  { id: '1', name: 'Smartphone X Pro', price: 799.99, imageUrl: '/images/product-x.jpg', rating: 4.5, reviews: 120 },
  { id: '2', name: 'Smartphone Y Lite', price: 499.99, imageUrl: '/images/product-y.jpg', rating: 4.0, reviews: 85 },
  { id: '3', name: 'Smartphone Z Ultra', price: 1099.99, imageUrl: '/images/product-z.jpg', rating: 4.8, reviews: 210 },
  { id: '4', name: 'Smartphone A Mini', price: 349.99, imageUrl: '/images/product-a.jpg', rating: 3.9, reviews: 50 },
  { id: '5', name: 'Smartphone B Plus', price: 649.99, imageUrl: '/images/product-b.jpg', rating: 4.2, reviews: 95 },
  { id: '6', name: 'Smartphone C Max', price: 899.99, imageUrl: '/images/product-c.jpg', rating: 4.6, reviews: 150 },
  { id: '7', name: 'Smartphone D Go', price: 299.99, imageUrl: '/images/product-d.jpg', rating: 3.7, reviews: 30 },
  { id: '8', name: 'Smartphone E Prime', price: 599.99, imageUrl: '/images/product-e.jpg', rating: 4.3, reviews: 110 },
];

// Product Card Component
const ProductCard: React.FC<{ product: Product }> = ({ product }) => (
  <Link href={`/product-detail-page?id=${product.id}`} className="block">
    <div
      className="bg-white shadow-md p-4 flex flex-col h-full transition-all duration-300 hover:shadow-lg hover:scale-[1.02]"
      style={{ borderRadius: borderRadius }}
    >
      <div className="relative w-full h-32 bg-gray-100 rounded-lg overflow-hidden mb-4">
        <Image
          src={product.imageUrl}
          alt={product.name}
          layout="fill"
          objectFit="contain"
          className="p-2"
        />
      </div>
      <h3 className="text-lg font-semibold text-gray-800 mb-1">{product.name}</h3>
      <div className="flex items-center text-sm text-gray-600 mb-2">
        <div className="flex items-center mr-2">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              size={16}
              fill={i < Math.floor(product.rating) ? secondaryColor : 'currentColor'}
              strokeWidth={1}
              className={i < Math.floor(product.rating) ? 'text-yellow-400' : 'text-gray-300'}
            />
          ))}
          <span className="ml-1">{product.rating.toFixed(1)}</span>
        </div>
        <span className="text-gray-500">({product.reviews} reviews)</span>
      </div>
      <p className="text-xl font-bold text-gray-900 mt-auto">${product.price.toFixed(2)}</p>
      <button
        className="mt-4 w-full py-2 px-4 text-white font-semibold rounded-lg transition-all duration-300 hover:opacity-90"
        style={{ backgroundColor: secondaryColor, borderRadius: '0.75rem' }} // Slightly smaller radius for button
        onClick={(e) => {
          e.preventDefault(); // Prevent navigating to product detail page
          e.stopPropagation(); // Prevent navigating to product detail page
          alert(`Added ${product.name} to cart!`);
        }}
      >
        Add to Cart
      </button>
    </div>
  </Link>
);

export default function ProductListingPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
      {/* Header */}
      <header
        className="w-full py-4 px-6 flex items-center justify-between shadow-md z-10"
        style={{ backgroundColor: primaryColor, height: '80px' }}
      >
        <div className="flex items-center gap-8">
          <Link href="/homepage" className="text-white text-2xl font-bold tracking-tight">
            E-Shop
          </Link>
          <nav className="hidden md:flex gap-6 text-white text-lg">
            <Link href="/category-page" className="hover:text-secondary transition-colors duration-300">Shop</Link>
            <Link href="/category-page" className="hover:text-secondary transition-colors duration-300">Categories</Link>
            <Link href="#" className="hover:text-secondary transition-colors duration-300">Deals</Link>
            <Link href="#" className="hover:text-secondary transition-colors duration-300">About Us</Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              className="py-2 pl-10 pr-4 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-secondary transition-all duration-300"
              style={{ borderRadius: '0.75rem' }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          </div>
          <Link href="/login-/-register-page" className="p-2 rounded-lg text-white hover:bg-gray-700 transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>
            <User size={24} />
          </Link>
          <Link href="/shopping-cart-page" className="relative p-2 rounded-lg text-white hover:bg-gray-700 transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>
            <ShoppingCart size={24} />
            <span className="absolute -top-1 -right-1 bg-secondary text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
              3
            </span>
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-grow container mx-auto px-6 py-8 grid grid-cols-1 md:grid-cols-[250px_1fr] gap-8">
        {/* Breadcrumbs and Page Title (above sidebar/main grid) */}
        <div className="col-span-full mb-4">
          <p className="text-sm text-gray-600 mb-2">
            <Link href="/homepage" className="hover:underline">Home</Link> &gt; <Link href="/category-page" className="hover:underline">Electronics</Link> &gt; <span className="font-medium">Smartphones</span>
          </p>
          <h1 className="text-4xl font-extrabold text-gray-900">Smartphones</h1>
        </div>

        {/* Sidebar */}
        <aside className="bg-white p-6 rounded-xl shadow-sm" style={{ borderRadius: borderRadius }}>
          <h2 className="text-xl font-bold text-gray-800 mb-4">Categories</h2>
          <nav className="space-y-2 mb-8">
            <Link href="/category-page?category=android" className="block text-gray-700 hover:text-secondary transition-colors duration-300">Android Phones</Link>
            <Link href="/category-page?category=iphone" className="block text-gray-700 hover:text-secondary transition-colors duration-300">iPhones</Link>
            <Link href="/category-page?category=feature" className="block text-gray-700 hover:text-secondary transition-colors duration-300">Feature Phones</Link>
          </nav>

          <h2 className="text-xl font-bold text-gray-800 mb-4">Filters</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Price Range</h3>
              <div className="w-full h-10 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500 text-sm">
                Price Range Slider (Placeholder)
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Brand</h3>
              <div className="space-y-2">
                <label className="flex items-center text-gray-700">
                  <input type="checkbox" className="mr-2 rounded text-secondary focus:ring-secondary" /> Samsung
                </label>
                <label className="flex items-center text-gray-700">
                  <input type="checkbox" className="mr-2 rounded text-secondary focus:ring-secondary" /> Apple
                </label>
                <label className="flex items-center text-gray-700">
                  <input type="checkbox" className="mr-2 rounded text-secondary focus:ring-secondary" /> Google
                </label>
                <label className="flex items-center text-gray-700">
                  <input type="checkbox" className="mr-2 rounded text-secondary focus:ring-secondary" /> Xiaomi
                </label>
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Color</h3>
              <div className="flex gap-2">
                <button className="w-8 h-8 rounded-full bg-black border-2 border-transparent hover:border-secondary transition-all duration-300"></button>
                <button className="w-8 h-8 rounded-full bg-white border-2 border-gray-300 hover:border-secondary transition-all duration-300"></button>
                <button className="w-8 h-8 rounded-full bg-blue-600 border-2 border-transparent hover:border-secondary transition-all duration-300"></button>
                <button className="w-8 h-8 rounded-full bg-red-600 border-2 border-transparent hover:border-secondary transition-all duration-300"></button>
              </div>
            </div>
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Storage Size</h3>
              <div className="flex flex-wrap gap-2">
                {['64GB', '128GB', '256GB', '512GB'].map((size) => (
                  <label key={size} className="inline-flex items-center">
                    <input type="radio" name="size" value={size} className="hidden peer" />
                    <span className="px-3 py-1 border border-gray-300 rounded-lg text-gray-700 cursor-pointer peer-checked:bg-secondary peer-checked:text-white peer-checked:border-secondary transition-all duration-300">
                      {size}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Product Grid */}
        <main className="flex flex-col">
          <div className="flex justify-end items-center mb-6">
            <label htmlFor="sort-by" className="text-gray-700 mr-2">Sort By:</label>
            <div className="relative">
              <select
                id="sort-by"
                className="appearance-none bg-white border border-gray-300 text-gray-800 py-2 pl-4 pr-10 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary transition-all duration-300"
                style={{ borderRadius: '0.75rem' }}
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="newest">Newest</option>
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
                <option value="rating-desc">Rating</option>
              </select>
              <ChevronDown size={20} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>

          {/* Pagination */}
          <div className="mt-12 flex justify-center items-center gap-4 text-lg">
            <button className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>Previous</button>
            <Link href="#" className="px-4 py-2 rounded-lg bg-secondary text-white font-semibold transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>1</Link>
            <Link href="#" className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>2</Link>
            <Link href="#" className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>3</Link>
            <span className="text-gray-600">...</span>
            <Link href="#" className="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors duration-300" style={{ borderRadius: '0.75rem' }}>Next</Link>
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer
        className="w-full py-8 px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-white text-sm"
        style={{ backgroundColor: primaryColor, height: '100px' }}
      >
        <p className="text-center md:text-left">© 2023 E-commerce Site. All rights reserved.</p>
        <nav className="flex flex-wrap justify-center md:justify-start gap-4 md:gap-6">
          <Link href="#" className="hover:text-secondary transition-colors duration-300">About Us</Link>
          <Link href="#" className="hover:text-secondary transition-colors duration-300">Contact</Link>
          <Link href="#" className="hover:text-secondary transition-colors duration-300">FAQ</Link>
          <Link href="#" className="hover:text-secondary transition-colors duration-300">Privacy Policy</Link>
        </nav>
        <div className="flex items-center gap-4">
          {/* Social Icons Placeholder */}
          <div className="flex gap-2">
            <span className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-secondary transition-colors duration-300">F</span>
            <span className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-secondary transition-colors duration-300">T</span>
            <span className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-secondary transition-colors duration-300">I</span>
          </div>
          <div className="flex">
            <input
              type="email"
              placeholder="Email for Newsletter"
              className="py-2 px-4 rounded-l-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-secondary transition-all duration-300"
              style={{ borderTopLeftRadius: '0.75rem', borderBottomLeftRadius: '0.75rem' }}
            />
            <button
              className="py-2 px-4 text-white font-semibold rounded-r-lg transition-all duration-300 hover:opacity-90"
              style={{ backgroundColor: secondaryColor, borderTopRightRadius: '0.75rem', borderBottomRightRadius: '0.75rem' }}
            >
              Subscribe
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}