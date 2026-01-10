"use client";

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ShoppingCart, User, Heart, Star } from 'lucide-react'; // Using Lucide for icons

// Mock Product Data - In a real application, this would come from an API call
const mockProduct = {
  id: '1',
  name: 'iPhone 15 Pro Max 256GB',
  brand: 'Apple',
  price: 1299.00,
  rating: 4.8,
  reviews: 120,
  shortDescription: 'Experience the pinnacle of smartphone technology with the iPhone 15 Pro Max. Featuring a stunning Super Retina XDR display, the powerful A17 Bionic chip, and an advanced camera system for unparalleled photos and videos.',
  longDescription: 'The iPhone 15 Pro Max redefines what\'s possible in a smartphone. Its aerospace-grade titanium design is both lightweight and durable. The revolutionary A17 Bionic chip delivers pro-level performance and efficiency, while the most advanced camera system ever in an iPhone captures incredible detail and vibrant colors, even in low light. Enjoy all-day battery life, a customizable Action Button, and the blazing-fast speed of 5G connectivity. Available in multiple stunning finishes.',
  specifications: [
    { label: 'Display', value: '6.7-inch Super Retina XDR' },
    { label: 'Processor', value: 'A17 Bionic chip' },
    { label: 'Storage', value: '256GB, 512GB, 1TB' },
    { label: 'Camera', value: 'Pro camera system (48MP Main, 12MP Ultra Wide, 12MP Telephoto)' },
    { label: 'Battery', value: 'All-day battery life' },
    { label: 'Material', value: 'Aerospace-grade titanium' },
  ],
  colors: [
    { name: 'Space Black', hex: '#333333', image: '/images/iphone-black.webp' },
    { name: 'Natural Titanium', hex: '#A8A8A0', image: '/images/iphone-titanium.webp' },
    { name: 'White Titanium', hex: '#F0F2F5', image: '/images/iphone-white.webp' },
    { name: 'Blue Titanium', hex: '#5F6A7B', image: '/images/iphone-blue.webp' },
  ],
  storageOptions: ['256GB', '512GB', '1TB'],
  images: [
    '/images/iphone-black.webp', // Main image
    '/images/iphone-titanium.webp',
    '/images/iphone-white.webp',
    '/images/iphone-blue.webp',
    '/images/iphone-detail-1.webp', // Additional detail images
    '/images/iphone-detail-2.webp',
  ],
  inStock: true,
  deliveryEstimate: '3-5 days',
};

// Mock Related Products - In a real application, this would come from an API call
const mockRelatedProducts = [
  { id: 'r1', name: 'Apple Watch Series 9', price: 399.00, image: '/images/apple-watch.webp' },
  { id: 'r2', name: 'AirPods Pro (2nd Gen)', price: 249.00, image: '/images/airpods-pro.webp' },
  { id: 'r3', name: 'MacBook Air M2', price: 1199.00, image: '/images/macbook-air.webp' },
  { id: 'r4', name: 'iPad Pro M4', price: 799.00, image: '/images/ipad-pro.webp' },
];

// Design Tokens (Tailwind equivalents for convenience)
const primaryBg = 'bg-[#0f172a]'; // primary: #0f172a
const secondaryBg = 'bg-[#3b82f6]'; // secondary: #3b82f6
const radiusClass = 'rounded-xl'; // radius: 1rem

// Helper to render star ratings
const renderStars = (rating: number) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

  return (
    <div className="flex items-center">
      {[...Array(fullStars)].map((_, i) => (
        <Star key={`full-${i}`} size={16} fill="#facc15" stroke="#facc15" />
      ))}
      {hasHalfStar && <Star key="half" size={16} fill="#facc15" stroke="#facc15" className="[clip-path:inset(0_50%_0_0)]" />} {/* Simple half star */}
      {[...Array(emptyStars)].map((_, i) => (
        <Star key={`empty-${i}`} size={16} stroke="#facc15" className="text-gray-300" />
      ))}
    </div>
  );
};

export default function ProductDetailPage() {
  const [mainImage, setMainImage] = useState(mockProduct.images[0]);
  const [selectedColor, setSelectedColor] = useState(mockProduct.colors[0].name);
  const [selectedStorage, setSelectedStorage] = useState(mockProduct.storageOptions[0]);
  const [quantity, setQuantity] = useState(1);
  const [activeTab, setActiveTab] = useState('Description'); // 'Description', 'Specifications', 'Reviews', 'Q&A'

  // Placeholder for API calls (as per strict rules, but not implemented for mock data)
  // In a real app, you'd import `api` from `@/lib/api`
  // import { api } from '@/lib/api';

  const handleAddToCart = async () => {
    console.log('Adding to cart:', {
      productId: mockProduct.id,
      color: selectedColor,
      storage: selectedStorage,
      quantity,
    });
    // Example API call structure:
    // try {
    //   const response = await api.post('/api/cart/add', {
    //     productId: mockProduct.id,
    //     color: selectedColor,
    //     storage: selectedStorage,
    //     quantity,
    //   });
    //   console.log('Added to cart successfully:', response.data);
    //   // Handle success, e.g., show a toast, update cart count
    // } catch (error) {
    //   console.error('Failed to add to cart:', error);
    //   // Handle error, e.g., show an error message
    // }
  };

  const handleBuyNow = async () => {
    console.log('Buying now:', {
      productId: mockProduct.id,
      color: selectedColor,
      storage: selectedStorage,
      quantity,
    });
    // Example API call structure:
    // try {
    //   const response = await api.post('/api/checkout/buy-now', {
    //     productId: mockProduct.id,
    //     color: selectedColor,
    //     storage: selectedStorage,
    //     quantity,
    //   });
    //   console.log('Initiated checkout:', response.data);
    //   // router.push('/checkout-page'); // Redirect to checkout page
    // } catch (error) {
    //   console.error('Failed to initiate checkout:', error);
    //   // Handle error
    // }
  };

  const handleAddToWishlist = () => {
    console.log('Adding to wishlist:', mockProduct.id);
    // API call to add to wishlist
    // try {
    //   await api.post('/api/wishlist/add', { productId: mockProduct.id });
    //   console.log('Added to wishlist');
    // } catch (error) {
    //   console.error('Failed to add to wishlist:', error);
    // }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
      {/* Header */}
      <header className={`w-full ${primaryBg} p-4 shadow-lg flex items-center justify-between z-10`} style={{ height: 80 }}>
        <div className="flex items-center space-x-8">
          <Link href="/homepage" className="text-2xl font-bold text-white">
            E-Shop
          </Link>
          <nav className="hidden md:flex space-x-6 text-lg">
            <Link href="/product-listing-page" className="text-white/80 hover:text-white transition-colors duration-300">Shop</Link>
            <Link href="/category-page" className="text-white/80 hover:text-white transition-colors duration-300">Categories</Link>
            <Link href="#" className="text-white/80 hover:text-white transition-colors duration-300">Deals</Link>
            <Link href="#" className="text-white/80 hover:text-white transition-colors duration-300">About Us</Link>
          </nav>
        </div>
        <div className="flex items-center space-x-4">
          <input
            type="text"
            placeholder="Search..."
            className={`px-4 py-2 ${radiusClass} bg-white/10 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-300`}
            style={{ width: 250, height: 32 }}
          />
          <button className={`p-2 ${radiusClass} bg-white/10 hover:bg-white/20 transition-all duration-300`}>
            <User className="text-white" size={20} />
          </button>
          <Link href="/shopping-cart-page" className={`relative p-2 ${radiusClass} bg-white/10 hover:bg-white/20 transition-all duration-300 flex items-center`}>
            <ShoppingCart className="text-white" size={20} />
            <span className="ml-2 text-white hidden sm:inline">Cart</span>
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">3</span>
          </Link>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-8">
        {/* Breadcrumbs */}
        <nav className="text-sm text-gray-600 mb-6">
          <Link href="/homepage" className="hover:underline">Home</Link> &gt;
          <Link href="/category-page" className="hover:underline">Electronics</Link> &gt;
          <Link href="/product-listing-page" className="hover:underline">Smartphones</Link> &gt;
          <span className="font-semibold">iPhone 15</span>
        </nav>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Product Images */}
          <div className="flex flex-col items-center">
            <div className={`w-full max-w-[680px] h-[400px] bg-gray-200 ${radiusClass} overflow-hidden shadow-lg mb-4 relative`}>
              <Image
                src={mainImage}
                alt={mockProduct.name}
                fill
                style={{ objectFit: 'contain' }}
                className="transition-opacity duration-300 ease-in-out"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                priority
              />
            </div>
            <div className="flex space-x-4 overflow-x-auto pb-2">
              {mockProduct.images.slice(0, 4).map((img, index) => (
                <button
                  key={index}
                  onClick={() => setMainImage(img)}
                  className={`w-[164px] h-[64px] flex-shrink-0 bg-gray-200 ${radiusClass} overflow-hidden border-2 ${mainImage === img ? 'border-blue-500' : 'border-transparent'} hover:border-blue-400 transition-all duration-300`}
                >
                  <Image
                    src={img}
                    alt={`${mockProduct.name} thumbnail ${index + 1}`}
                    width={164}
                    height={64}
                    style={{ objectFit: 'contain' }}
                    className="w-full h-full"
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Right Column: Product Details */}
          <div className="flex flex-col">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-2">{mockProduct.name}</h1>
            <p className="text-lg text-gray-700 mb-1">Brand: <span className="font-semibold">{mockProduct.brand}</span></p>
            <p className="text-5xl font-bold text-gray-900 mb-2">${mockProduct.price.toFixed(2)}</p>
            <div className="flex items-center mb-4">
              {renderStars(mockProduct.rating)}
              <span className="ml-2 text-gray-600">({mockProduct.reviews} Reviews)</span>
            </div>
            <p className="text-gray-700 leading-relaxed mb-6">{mockProduct.shortDescription}</p>

            {/* Options */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label htmlFor="color-select" className="block text-sm font-medium text-gray-700 mb-1">Color:</label>
                <select
                  id="color-select"
                  value={selectedColor}
                  onChange={(e) => setSelectedColor(e.target.value)}
                  className={`block w-full px-4 py-2 border border-gray-300 ${radiusClass} shadow-sm focus:ring-blue-500 focus:border-blue-500 transition-all duration-300`}
                  style={{ width: 200, height: 32 }}
                >
                  {mockProduct.colors.map((color) => (
                    <option key={color.name} value={color.name}>{color.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="storage-select" className="block text-sm font-medium text-gray-700 mb-1">Storage:</label>
                <select
                  id="storage-select"
                  value={selectedStorage}
                  onChange={(e) => setSelectedStorage(e.target.value)}
                  className={`block w-full px-4 py-2 border border-gray-300 ${radiusClass} shadow-sm focus:ring-blue-500 focus:border-blue-500 transition-all duration-300`}
                  style={{ width: 200, height: 32 }}
                >
                  {mockProduct.storageOptions.map((storage) => (
                    <option key={storage} value={storage}>{storage}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mb-6">
              <label htmlFor="quantity-input" className="block text-sm font-medium text-gray-700 mb-1">Quantity:</label>
              <input
                id="quantity-input"
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                className={`block w-[100px] px-4 py-2 border border-gray-300 ${radiusClass} shadow-sm focus:ring-blue-500 focus:border-blue-500 transition-all duration-300`}
                style={{ height: 32 }}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-4 mb-4">
              <button
                onClick={handleAddToCart}
                className={`flex-1 ${secondaryBg} hover:bg-blue-600 text-white font-bold py-3 px-6 ${radiusClass} shadow-md hover:shadow-lg transition-all duration-300`}
                style={{ width: 200, height: 48 }}
              >
                ADD TO CART
              </button>
              <button
                onClick={handleBuyNow}
                className={`flex-1 bg-gray-800 hover:bg-gray-900 text-white font-bold py-3 px-6 ${radiusClass} shadow-md hover:shadow-lg transition-all duration-300`}
                style={{ width: 200, height: 48 }}
              >
                BUY NOW
              </button>
              <button
                onClick={handleAddToWishlist}
                className={`p-3 ${radiusClass} bg-gray-200 hover:bg-gray-300 text-gray-700 transition-all duration-300 flex items-center justify-center`}
                style={{ width: 100, height: 48 }}
              >
                <Heart size={20} className="mr-1" /> Wishlist
              </button>
            </div>

            {/* Stock and Delivery Info */}
            <div className="text-lg mb-4">
              <p className="text-green-600 font-semibold mb-1">In Stock</p>
              <p className="text-gray-600">Est. Delivery: {mockProduct.deliveryEstimate}</p>
            </div>
          </div>
        </div>

        {/* Product Information Tabs */}
        <div className="mt-12">
          <div className="flex border-b border-gray-200 mb-6">
            {['Description', 'Specifications', 'Reviews', 'Q&A'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-3 px-6 text-lg font-semibold ${activeTab === tab ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600 hover:text-gray-800'} transition-all duration-300`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className={`bg-white p-6 ${radiusClass} shadow-md`}>
            {activeTab === 'Description' && (
              <div className="prose max-w-none">
                <h2 className="text-2xl font-bold mb-4">Product Overview</h2>
                <p className="text-gray-800 leading-relaxed">{mockProduct.longDescription}</p>
                <h3 className="text-xl font-semibold mt-6 mb-3">Key Features:</h3>
                <ul className="list-disc list-inside text-gray-700">
                  <li>Aerospace-grade titanium design</li>
                  <li>A17 Bionic chip for ultimate performance</li>
                  <li>Advanced Pro camera system</li>
                  <li>All-day battery life</li>
                  <li>Customizable Action Button</li>
                </ul>
              </div>
            )}
            {activeTab === 'Specifications' && (
              <div className="prose max-w-none">
                <h2 className="text-2xl font-bold mb-4">Technical Specifications</h2>
                <table className="min-w-full divide-y divide-gray-200">
                  <tbody className="bg-white divide-y divide-gray-200">
                    {mockProduct.specifications.map((spec, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{spec.label}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{spec.value}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {activeTab === 'Reviews' && (
              <div>
                <h2 className="text-2xl font-bold mb-4">Customer Reviews ({mockProduct.reviews})</h2>
                <p className="text-gray-700">This section would display a list of customer reviews, ratings, and options to submit a new review.</p>
                {/* Example review card */}
                <div className={`mt-4 p-4 bg-gray-50 ${radiusClass} shadow-sm`}>
                  <div className="flex items-center mb-2">
                    {renderStars(5)}
                    <span className="ml-2 font-semibold">Excellent product!</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">John Doe - 2 days ago</p>
                  <p className="text-gray-800">"Absolutely love my new iPhone 15 Pro Max. The camera is incredible and the performance is unmatched. Highly recommend!"</p>
                </div>
              </div>
            )}
            {activeTab === 'Q&A' && (
              <div>
                <h2 className="text-2xl font-bold mb-4">Questions & Answers</h2>
                <p className="text-gray-700">This section would feature frequently asked questions about the product and allow users to ask new questions.</p>
                {/* Example Q&A */}
                <div className={`mt-4 p-4 bg-gray-50 ${radiusClass} shadow-sm`}>
                  <p className="font-semibold text-gray-900 mb-1">Q: Does this model support eSIM?</p>
                  <p className="text-gray-700">A: Yes, the iPhone 15 Pro Max supports dual eSIMs.</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Related Products */}
        <section className="mt-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Related Products</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {mockRelatedProducts.map((product) => (
              <Link href={`/product-detail-page?id=${product.id}`} key={product.id} className={`block bg-white ${radiusClass} shadow-md hover:shadow-lg transition-all duration-300 p-4 flex items-center space-x-4`}>
                <div className={`w-16 h-16 flex-shrink-0 bg-gray-100 ${radiusClass} overflow-hidden`}>
                  <Image src={product.image} alt={product.name} width={64} height={64} style={{ objectFit: 'contain' }} className="w-full h-full" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
                  <p className="text-blue-600 font-bold">${product.price.toFixed(2)}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className={`w-full ${primaryBg} p-8 text-white mt-12`} style={{ height: 100 }}>
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <p className="text-sm">&copy; 2023 E-commerce Site. All rights reserved.</p>
          <nav className="flex space-x-6 text-sm">
            <Link href="#" className="hover:text-white/80 transition-colors duration-300">About Us</Link>
            <Link href="#" className="hover:text-white/80 transition-colors duration-300">Contact</Link>
            <Link href="#" className="hover:text-white/80 transition-colors duration-300">FAQ</Link>
            <Link href="#" className="hover:text-white/80 transition-colors duration-300">Privacy</Link>
          </nav>
          <div className="flex items-center space-x-4">
            <span className="text-sm hidden sm:inline">Social Icons (e.g., Facebook, Twitter)</span>
            <input
              type="email"
              placeholder="Email for Newsletter"
              className={`px-3 py-1 ${radiusClass} bg-white/10 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all duration-300`}
              style={{ width: 200, height: 24 }}
            />
            <button className={`${secondaryBg} hover:bg-blue-600 text-white px-4 py-1 ${radiusClass} transition-all duration-300`} style={{ height: 24 }}>
              Subscribe
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}