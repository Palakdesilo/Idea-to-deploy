"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { Search, ShoppingCart, User, Menu } from "lucide-react";

// Design Tokens
const primaryColor = "#0f172a"; // slate-900
const secondaryColor = "#3b82f6"; // blue-500
const borderRadius = "1rem"; // rounded-xl

// Dummy Data (replace with API calls in a real application)
// In a real scenario, these would be fetched using the '@/lib/api' utility.
const featuredCategories = [
  { id: 1, name: "Electronics", image: "/images/category-electronics.jpg", link: "/category-page" },
  { id: 2, name: "Apparel", image: "/images/category-apparel.jpg", link: "/category-page" },
  { id: 3, name: "Home Goods", image: "/images/category-homegoods.jpg", link: "/category-page" },
];

const newArrivals = [
  { id: 1, name: "Wireless Headphones", price: "$199.99", image: "/images/product-headphones.jpg", link: "/product-detail-page" },
  { id: 2, name: "Smartwatch Pro", price: "$249.99", image: "/images/product-smartwatch.jpg", link: "/product-detail-page" },
  { id: 3, name: "Designer Backpack", price: "$89.99", image: "/images/product-backpack.jpg", link: "/product-detail-page" },
  { id: 4, name: "Portable Speaker", price: "$79.99", image: "/images/product-speaker.jpg", link: "/product-detail-page" },
];

export default function Homepage() {
  const [cartItemCount] = useState(3); // Example cart count, would come from global state/API
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
      {/* Header */}
      <header
        className="sticky top-0 z-50 w-full p-4 flex items-center justify-between shadow-md"
        style={{ backgroundColor: primaryColor, height: '80px' }} // Wireframe header height: 80
      >
        <div className="flex items-center gap-8">
          <Link href="/homepage" className="text-white text-2xl font-bold tracking-tight">
            Logo
          </Link>
          <nav className="hidden md:flex gap-6 text-white text-lg">
            <Link href="/product-listing-page" className="hover:text-secondary transition-colors duration-300">Shop</Link>
            <Link href="/category-page" className="hover:text-secondary transition-colors duration-300">Categories</Link>
            {/* These routes are placeholders as they are not in Available Routes */}
            <Link href="#" className="hover:text-secondary transition-colors duration-300">Deals</Link>
            <Link href="#" className="hover:text-secondary transition-colors duration-300">About Us</Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative hidden md:block">
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-secondary transition-all duration-300"
              style={{ borderRadius: borderRadius }}
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          </div>
          <Link
            href="/login-/-register-page" // Assuming User button leads to login/register
            className="p-2 text-white hover:text-secondary transition-colors duration-300 hidden md:block"
            aria-label="User Account"
          >
            <User size={24} />
          </Link>
          <Link
            href="/shopping-cart-page"
            className="relative p-2 text-white hover:text-secondary transition-colors duration-300"
            aria-label="Shopping Cart"
          >
            <ShoppingCart size={24} />
            {cartItemCount > 0 && (
              <span
                className="absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 text-xs font-bold text-white rounded-full"
                style={{ backgroundColor: secondaryColor }}
              >
                {cartItemCount}
              </span>
            )}
          </Link>
          <button
            className="md:hidden p-2 text-white"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Open Mobile Menu"
          >
            <Menu size={24} />
          </button>
        </div>
      </header>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <nav
          className="md:hidden flex flex-col gap-4 p-4 shadow-md animate-fade-in-down"
          style={{ backgroundColor: primaryColor }}
        >
          <Link href="/product-listing-page" className="text-white text-lg hover:text-secondary transition-colors duration-300" onClick={() => setIsMobileMenuOpen(false)}>Shop</Link>
          <Link href="/category-page" className="text-white text-lg hover:text-secondary transition-colors duration-300" onClick={() => setIsMobileMenuOpen(false)}>Categories</Link>
          <Link href="#" className="text-white text-lg hover:text-secondary transition-colors duration-300" onClick={() => setIsMobileMenuOpen(false)}>Deals</Link>
          <Link href="#" className="text-white text-lg hover:text-secondary transition-colors duration-300" onClick={() => setIsMobileMenuOpen(false)}>About Us</Link>
          <div className="relative w-full">
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-10 pr-4 py-2 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-secondary transition-all duration-300"
              style={{ borderRadius: borderRadius }}
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          </div>
          <Link
            href="/login-/-register-page"
            className="w-full p-2 text-white hover:text-secondary transition-colors duration-300 text-left flex items-center"
            aria-label="User Account"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <User size={24} className="inline-block mr-2" /> User Account
          </Link>
        </nav>
      )}

      <main className="flex-grow">
        {/* Hero Banner */}
        <section className="relative w-full h-[300px] overflow-hidden">
          <Image
            src="/images/hero-banner.jpg" // Placeholder image, ensure this path exists in your public folder
            alt="Amazing Deals Banner"
            layout="fill"
            objectFit="cover"
            quality={90}
            className="animate-fade-in"
          />
          <div className="absolute inset-0 bg-black bg-opacity-40 flex flex-col items-start justify-center p-6 md:p-24">
            <h1 className="text-white text-4xl md:text-5xl font-extrabold mb-4 animate-fade-in-up">
              Amazing Deals!
            </h1>
            <p className="text-white text-lg md:text-xl mb-6 max-w-md animate-fade-in-up delay-100">
              Discover our latest collections and unbeatable prices.
            </p>
            <Link href="/product-listing-page">
              <button
                className="px-8 py-3 text-lg font-semibold text-white rounded-lg shadow-lg hover:scale-105 transition-all duration-300 animate-fade-in-up delay-200"
                style={{ backgroundColor: secondaryColor, borderRadius: borderRadius }}
              >
                Shop Now
              </button>
            </Link>
          </div>
        </section>

        {/* Featured Categories */}
        <section className="container mx-auto px-6 py-12">
          <h2 className="text-3xl font-bold mb-8 text-gray-800">Featured Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {featuredCategories.map((category) => (
              <Link href={category.link} key={category.id}>
                <div
                  className="relative flex items-center justify-center h-40 overflow-hidden group cursor-pointer shadow-md hover:shadow-xl transition-all duration-300"
                  style={{ borderRadius: borderRadius }}
                >
                  <Image
                    src={category.image} // Placeholder image
                    alt={category.name}
                    layout="fill"
                    objectFit="cover"
                    className="group-hover:scale-105 transition-transform duration-500 ease-in-out"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-40 group-hover:bg-opacity-60 transition-opacity duration-300 flex items-center justify-center">
                    <h3 className="text-white text-2xl font-semibold z-10 group-hover:text-secondary transition-colors duration-300">
                      {category.name}
                    </h3>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* New Arrivals */}
        <section className="container mx-auto px-6 py-12">
          <h2 className="text-3xl font-bold mb-8 text-gray-800">New Arrivals</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {newArrivals.map((product) => (
              <Link href={product.link} key={product.id}>
                <div
                  className="bg-white p-4 shadow-lg hover:shadow-xl transition-all duration-300 flex flex-col items-center text-center group cursor-pointer h-full"
                  style={{ borderRadius: borderRadius }}
                >
                  <div className="relative w-full h-48 mb-4 overflow-hidden" style={{ borderRadius: `calc(${borderRadius} - 0.5rem)` }}>
                    <Image
                      src={product.image} // Placeholder image
                      alt={product.name}
                      layout="fill"
                      objectFit="cover"
                      className="group-hover:scale-105 transition-transform duration-500 ease-in-out"
                    />
                  </div>
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-secondary transition-colors duration-300">
                    {product.name}
                  </h3>
                  <p className="text-gray-700 text-lg font-bold">{product.price}</p>
                  <button
                    className="mt-4 px-6 py-2 text-sm font-medium text-white rounded-lg hover:scale-105 transition-all duration-300 opacity-0 group-hover:opacity-100"
                    style={{ backgroundColor: secondaryColor, borderRadius: borderRadius }}
                  >
                    Add to Cart
                  </button>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Promo Banner */}
        <section className="w-full h-[120px] relative overflow-hidden my-12">
          <Image
            src="/images/promo-banner.jpg" // Placeholder image
            alt="Limited Time Offer"
            layout="fill"
            objectFit="cover"
            quality={90}
            className="animate-fade-in"
          />
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <p className="text-white text-2xl md:text-3xl font-bold tracking-wide animate-pulse">
              Limited Time Offer: Get 20% Off Your First Order!
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer
        className="w-full p-8 text-white text-sm md:text-base"
        style={{ backgroundColor: primaryColor, height: '100px' }} // Wireframe footer height: 100
      >
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <p className="text-center md:text-left">© 2023 E-commerce Site. All rights reserved.</p>

          <nav className="flex flex-wrap justify-center md:justify-start gap-x-6 gap-y-2">
            {/* These routes are placeholders as they are not in Available Routes */}
            <Link href="#" className="hover:text-secondary transition-colors duration-300">About Us</Link>
            <Link href="#" className="hover:text-secondary transition-colors duration-300">Contact</Link>
            <Link href="#" className="hover:text-secondary transition-colors duration-300">FAQ</Link>
            <Link href="#" className="hover:text-secondary transition-colors duration-300">Privacy Policy</Link>
          </nav>

          <div className="flex items-center gap-4">
            <span className="hidden md:block">Social Icons:</span>
            {/* Placeholder for actual social icons */}
            <div className="flex gap-3">
              <Link href="#" aria-label="Facebook" className="hover:text-secondary transition-colors duration-300">FB</Link>
              <Link href="#" aria-label="Twitter" className="hover:text-secondary transition-colors duration-300">TW</Link>
              <Link href="#" aria-label="Instagram" className="hover:text-secondary transition-colors duration-300">IG</Link>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-2 items-center">
            <input
              type="email"
              placeholder="Email for Newsletter"
              className="px-4 py-2 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-secondary transition-all duration-300 w-full sm:w-auto"
              style={{ borderRadius: borderRadius }}
            />
            <button
              className="px-6 py-2 text-white rounded-lg hover:scale-105 transition-all duration-300 w-full sm:w-auto"
              style={{ backgroundColor: secondaryColor, borderRadius: borderRadius }}
            >
              Subscribe
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}