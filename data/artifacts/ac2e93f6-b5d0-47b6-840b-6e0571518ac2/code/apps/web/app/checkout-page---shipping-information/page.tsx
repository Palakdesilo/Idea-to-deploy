"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  User,
  MapPin,
  Mail,
  Phone,
  Building,
  Globe,
  ChevronRight,
  Package,
  Truck,
  CreditCard,
  CheckCircle,
} from "lucide-react";

// Mock API utility - In a real production app, this would be from '@/lib/api'
// For this task, we simulate its behavior.
const api = {
  post: async (url: string, data: any) => {
    console.log(`API POST request to ${url} with data:`, data);
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.1) { // Simulate 90% success rate
          resolve({ success: true, message: "Shipping information saved successfully!" });
        } else {
          reject(new Error("Failed to save shipping information. Please try again."));
        }
      }, 1500); // Simulate network delay
    });
  },
};

// Zod schema for shipping information validation
const shippingSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  address1: z.string().min(1, "Address Line 1 is required"),
  address2: z.string().optional(),
  city: z.string().min(1, "City is required"),
  state: z.string().min(1, "State/Province is required"),
  zipCode: z.string().min(1, "Zip/Postal Code is required"),
  country: z.string().min(1, "Country is required"),
  phone: z.string().min(1, "Phone number is required").regex(/^\+?[1-9]\d{1,14}$/, "Invalid phone number format (e.g., +1234567890)"),
  email: z.string().email("Invalid email address"),
  useAsBilling: z.boolean(),
  shippingMethod: z.enum(["standard", "express"]),
});

type ShippingFormValues = z.infer<typeof shippingSchema>;

// Reusable Input Component for form fields
interface InputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  name: keyof ShippingFormValues;
  icon?: React.ElementType; // Lucide React Icon component
  error?: string;
  register: any; // react-hook-form's register function
}

const InputField: React.FC<InputFieldProps> = ({ label, name, icon: Icon, error, register, ...props }) => (
  <div className="mb-4">
    <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
      {label}
    </label>
    <div className="relative">
      {Icon && (
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Icon className="h-5 w-5 text-gray-400" aria-hidden="true" />
        </div>
      )}
      <input
        id={name}
        {...register(name)}
        className={`block w-full pl-${Icon ? '10' : '3'} pr-3 py-2 border ${error ? "border-red-500" : "border-gray-300"
          } rounded-xl shadow-sm focus:outline-none focus:ring-[#3b82f6] focus:border-[#3b82f6] sm:text-sm transition-all duration-200`}
        {...props}
      />
    </div>
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

// Mock Data for Order Summary
const mockOrderItems = [
  { id: 'prod1', name: 'Premium Wireless Headphones', qty: 1, price: 199.99 },
  { id: 'prod2', name: 'Ergonomic Mechanical Keyboard', qty: 1, price: 129.99 },
  { id: 'prod3', name: 'Ultra-wide Curved Monitor', qty: 1, price: 499.99 },
];
const subtotal = mockOrderItems.reduce((acc, item) => acc + item.qty * item.price, 0);
const shippingCostStandard = 9.99;
const shippingCostExpress = 24.99;
const taxRate = 0.05; // 5%
const tax = subtotal * taxRate;

export default function CheckoutShippingPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<ShippingFormValues>({
    resolver: zodResolver(shippingSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      address1: "",
      address2: "",
      city: "",
      state: "",
      zipCode: "",
      country: "",
      phone: "",
      email: "",
      useAsBilling: false,
      shippingMethod: "standard", // Default selected shipping method
    },
  });

  // Watch for shipping method changes to dynamically update the total
  const currentShippingMethod = watch("shippingMethod");
  const currentShippingCost = currentShippingMethod === "express" ? shippingCostExpress : shippingCostStandard;
  const total = subtotal + currentShippingCost + tax;

  const onSubmit: SubmitHandler<ShippingFormValues> = async (data) => {
    setIsLoading(true);
    try {
      await api.post("/api/checkout/shipping", data);
      console.log("Shipping information submitted successfully:", data);
      // Redirect to the next step in checkout flow
      // As per available routes, '/checkout-page' is the closest generic checkout route.
      // Ideally, this would be a more specific route like '/checkout-page---payment-information'.
      router.push("/checkout-page");
    } catch (error: any) {
      console.error("Submission error:", error.message);
      alert(error.message); // Simple alert for error display
    } finally {
      setIsLoading(false);
    }
  };

  // Handler for radio button changes to update react-hook-form state
  const handleShippingMethodChange = (method: "standard" | "express") => {
    setValue("shippingMethod", method);
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-slate-800">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-4 bg-white shadow-sm h-20">
        <Link href="/homepage" className="text-3xl font-extrabold text-[#0f172a] hover:text-[#3b82f6] transition-colors duration-300">
          E-Shop
        </Link>
        <div className="flex items-center space-x-4 text-sm font-medium">
          <span className="text-[#3b82f6] font-semibold flex items-center">
            <Package size={18} className="mr-2" /> Shipping
          </span>
          <ChevronRight size={16} className="text-gray-400" />
          <span className="text-gray-500 flex items-center">
            <CreditCard size={18} className="mr-2" /> Payment
          </span>
          <ChevronRight size={16} className="text-gray-400" />
          <span className="text-gray-500 flex items-center">
            <CheckCircle size={18} className="mr-2" /> Review
          </span>
          <ChevronRight size={16} className="text-gray-400" />
          <span className="text-gray-500 flex items-center">Confirmation</span>
        </div>
      </header>

      {/* Main Content Area - Two-column layout */}
      <main className="flex-grow container mx-auto p-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Shipping Form */}
        <section className="bg-white/50 backdrop-blur-lg p-8 rounded-xl shadow-lg border border-white/20 animate-fade-in">
          <h1 className="text-3xl font-bold text-[#0f172a] mb-6">Shipping Information</h1>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="First Name"
                name="firstName"
                icon={User}
                register={register}
                error={errors.firstName?.message}
                placeholder="John"
              />
              <InputField
                label="Last Name"
                name="lastName"
                icon={User}
                register={register}
                error={errors.lastName?.message}
                placeholder="Doe"
              />
            </div>

            <InputField
              label="Address Line 1"
              name="address1"
              icon={MapPin}
              register={register}
              error={errors.address1?.message}
              placeholder="123 Main St"
            />
            <InputField
              label="Address Line 2 (Optional)"
              name="address2"
              icon={Building}
              register={register}
              error={errors.address2?.message}
              placeholder="Apt, Suite, Bldg (Optional)"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="City"
                name="city"
                icon={MapPin}
                register={register}
                error={errors.city?.message}
                placeholder="New York"
              />
              <InputField
                label="State/Province"
                name="state"
                icon={MapPin}
                register={register}
                error={errors.state?.message}
                placeholder="NY"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Zip/Postal Code"
                name="zipCode"
                icon={MapPin}
                register={register}
                error={errors.zipCode?.message}
                placeholder="10001"
              />
              <InputField
                label="Country"
                name="country"
                icon={Globe}
                register={register}
                error={errors.country?.message}
                placeholder="United States"
              />
            </div>

            <InputField
              label="Phone Number"
              name="phone"
              icon={Phone}
              register={register}
              error={errors.phone?.message}
              type="tel"
              placeholder="+1 (555) 123-4567"
            />
            <InputField
              label="Email"
              name="email"
              icon={Mail}
              register={register}
              error={errors.email?.message}
              type="email"
              placeholder="john.doe@example.com"
            />

            <div className="flex items-center mt-6">
              <input
                id="useAsBilling"
                type="checkbox"
                {...register("useAsBilling")}
                className="h-4 w-4 text-[#3b82f6] border-gray-300 rounded focus:ring-[#3b82f6]"
              />
              <label htmlFor="useAsBilling" className="ml-2 block text-sm text-gray-900">
                Use as billing address
              </label>
            </div>

            <div className="mt-8">
              <h3 className="text-lg font-semibold text-[#0f172a] mb-4">Shipping Method Selection</h3>
              <div className="space-y-4">
                <label
                  htmlFor="standardShipping"
                  className={`flex items-center p-4 border rounded-xl cursor-pointer transition-all duration-200 ${currentShippingMethod === "standard"
                      ? "border-[#3b82f6] ring-2 ring-[#3b82f6] bg-blue-50"
                      : "border-gray-300 hover:border-gray-400"
                    }`}
                >
                  <input
                    type="radio"
                    id="standardShipping"
                    value="standard"
                    {...register("shippingMethod")}
                    checked={currentShippingMethod === "standard"}
                    onChange={() => handleShippingMethodChange("standard")}
                    className="h-4 w-4 text-[#3b82f6] focus:ring-[#3b82f6] border-gray-300"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-900 flex-grow">Standard Shipping</span>
                  <span className="text-sm font-semibold text-gray-700">${shippingCostStandard.toFixed(2)}</span>
                </label>

                <label
                  htmlFor="expressShipping"
                  className={`flex items-center p-4 border rounded-xl cursor-pointer transition-all duration-200 ${currentShippingMethod === "express"
                      ? "border-[#3b82f6] ring-2 ring-[#3b82f6] bg-blue-50"
                      : "border-gray-300 hover:border-gray-400"
                    }`}
                >
                  <input
                    type="radio"
                    id="expressShipping"
                    value="express"
                    {...register("shippingMethod")}
                    checked={currentShippingMethod === "express"}
                    onChange={() => handleShippingMethodChange("express")}
                    className="h-4 w-4 text-[#3b82f6] focus:ring-[#3b82f6] border-gray-300"
                  />
                  <span className="ml-3 text-sm font-medium text-gray-900 flex-grow">Express Shipping</span>
                  <span className="text-sm font-semibold text-gray-700">${shippingCostExpress.toFixed(2)}</span>
                </label>
                {errors.shippingMethod && (
                  <p className="mt-1 text-sm text-red-600">{errors.shippingMethod.message}</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              className={`w-full flex justify-center items-center py-3 px-6 border border-transparent rounded-xl shadow-sm text-lg font-medium text-white bg-[#3b82f6] hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#3b82f6] transition-all duration-300 ${isLoading ? "opacity-70 cursor-not-allowed animate-pulse" : ""
                }`}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Processing...
                </>
              ) : (
                "Continue to Payment"
              )}
            </button>
          </form>
        </section>

        {/* Right Column: Order Summary */}
        <aside className="bg-white/50 backdrop-blur-lg p-8 rounded-xl shadow-lg border border-white/20 animate-fade-in">
          <h2 className="text-2xl font-bold text-[#0f172a] mb-6">Order Summary</h2>

          <div className="space-y-4 mb-6">
            {mockOrderItems.map((item) => (
              <div key={item.id} className="flex justify-between items-center text-gray-700">
                <span className="text-base">
                  {item.name} x {item.qty}
                </span>
                <span className="font-medium">${(item.qty * item.price).toFixed(2)}</span>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-200 pt-6 space-y-3">
            <div className="flex justify-between text-gray-700">
              <span>Subtotal:</span>
              <span className="font-medium">${subtotal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-700">
              <span>Shipping:</span>
              <span className="font-medium">${currentShippingCost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-gray-700">
              <span>Tax:</span>
              <span className="font-medium">${tax.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center text-xl font-bold text-[#0f172a] border-t border-gray-300 pt-4 mt-4">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
          </div>
        </aside>
      </main>

      {/* Footer */}
      <footer className="bg-[#0f172a] text-white p-6 text-center h-24 flex items-center justify-center">
        <p className="text-sm">
          &copy; {new Date().getFullYear()} E-Shop. All rights reserved.{" "}
          <Link href="#" className="underline hover:text-[#3b82f6] transition-colors duration-300">
            Privacy Policy
          </Link>
        </p>
      </footer>
    </div>
  );
}