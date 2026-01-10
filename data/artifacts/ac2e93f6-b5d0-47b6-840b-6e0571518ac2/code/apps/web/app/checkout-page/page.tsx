"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

// Assuming shadcn/ui components are available at these paths
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { toast } from 'react-hot-toast'; // Assuming a toast notification library like react-hot-toast

// Mock API utility - In a real application, this would be from '@/lib/api'
// For demonstration, it simulates an async API call.
const api = {
  post: async (url: string, data: any) => {
    console.log(`Mock API POST to ${url} with data:`, data);
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() > 0.1) { // Simulate 90% success rate
          resolve({ success: true, message: 'Order placed successfully!' });
        } else {
          reject(new Error('Failed to place order. Please try again.'));
        }
      }, 1500); // Simulate network delay
    });
  },
};

// Design Tokens
const primaryColor = '#0f172a'; // Tailwind: slate-900
const secondaryColor = '#3b82f6'; // Tailwind: blue-500
const borderRadiusClass = 'rounded-xl'; // Corresponds to radius: '1rem'

// Zod schema for form validation
const checkoutFormSchema = z.object({
  fullName: z.string().min(1, { message: 'Full Name is required' }),
  addressLine1: z.string().min(1, { message: 'Address Line 1 is required' }),
  cityStateZip: z.string().min(1, { message: 'City, State, Zip is required' }),
  country: z.string().min(1, { message: 'Country is required' }),
  phone: z.string()
    .min(10, { message: 'Phone number must be at least 10 digits' })
    .max(15, { message: 'Phone number cannot exceed 15 digits' })
    .regex(/^\+?[0-9\s\-()]*$/, { message: 'Invalid phone number format' }),
  email: z.string().email({ message: 'Valid Email is required' }),
  useAsBillingAddress: z.boolean().default(false),
  shippingMethod: z.enum(['standard', 'express'], { message: 'Please select a shipping method' }),
  paymentMethod: z.enum(['creditCard', 'paypal'], { message: 'Please select a payment method' }),
  cardNumber: z.string().optional(),
  expiryDate: z.string().optional(),
  cvv: z.string().optional(),
  cardholderName: z.string().optional(),
  agreeToTerms: z.boolean().refine(val => val === true, { message: 'You must agree to the Terms & Conditions' }),
}).superRefine((data, ctx) => {
  // Conditional validation for credit card fields
  if (data.paymentMethod === 'creditCard') {
    if (!data.cardNumber || data.cardNumber.trim() === '') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Card Number is required for Credit Card payment',
        path: ['cardNumber'],
      });
    } else if (!/^\d{13,19}$/.test(data.cardNumber.replace(/\s/g, ''))) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Invalid Card Number',
        path: ['cardNumber'],
      });
    }
    if (!data.expiryDate || data.expiryDate.trim() === '') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Expiry Date is required for Credit Card payment',
        path: ['expiryDate'],
      });
    } else if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(data.expiryDate)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Invalid Expiry Date (MM/YY)',
        path: ['expiryDate'],
      });
    }
    if (!data.cvv || data.cvv.trim() === '') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'CVV is required for Credit Card payment',
        path: ['cvv'],
      });
    } else if (!/^\d{3,4}$/.test(data.cvv)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Invalid CVV',
        path: ['cvv'],
      });
    }
    if (!data.cardholderName || data.cardholderName.trim() === '') {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Cardholder Name is required for Credit Card payment',
        path: ['cardholderName'],
      });
    }
  }
});

type CheckoutFormValues = z.infer<typeof checkoutFormSchema>;

// Mock product data for order summary
const mockCartItems = [
  { id: 'p1', name: 'Premium Wireless Headphones', quantity: 1, price: 100.00 },
  { id: 'p2', name: 'Ergonomic Mechanical Keyboard', quantity: 2, price: 50.00 },
  { id: 'p3', name: 'High-Resolution Webcam', quantity: 1, price: 20.00 },
];

export default function CheckoutPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CheckoutFormValues>({
    resolver: zodResolver(checkoutFormSchema),
    defaultValues: {
      fullName: '',
      addressLine1: '',
      cityStateZip: '',
      country: '',
      phone: '',
      email: '',
      useAsBillingAddress: false,
      shippingMethod: 'standard', // Default to standard shipping
      paymentMethod: 'creditCard', // Default to credit card
      agreeToTerms: false,
    },
  });

  const selectedShippingMethod = watch('shippingMethod');
  const selectedPaymentMethod = watch('paymentMethod');

  const calculateOrderSummary = () => {
    const subtotal = mockCartItems.reduce((sum, item) => sum + item.quantity * item.price, 0);
    const shippingCost = selectedShippingMethod === 'express' ? 15.00 : 5.00;
    const taxRate = 0.07; // 7% tax
    const tax = (subtotal + shippingCost) * taxRate;
    const total = subtotal + shippingCost + tax;
    return { subtotal, shippingCost, tax, total };
  };

  const { subtotal, shippingCost, tax, total } = calculateOrderSummary();

  const onSubmit = async (data: CheckoutFormValues) => {
    setIsLoading(true);
    try {
      // In a real app, you'd send this data to your backend
      await api.post('/api/checkout/place-order', data);
      toast.success('Order placed successfully!');
      // Redirect to a confirmation page or the next step in the checkout flow
      router.push('/checkout-page---shipping-information');
    } catch (error: any) {
      console.error('Checkout error:', error);
      toast.error(error.message || 'An unexpected error occurred during checkout.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-800">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6 flex justify-between items-center" style={{ height: '80px' }}>
        <Link href="/homepage" className="text-2xl font-bold text-gray-900 transition-colors duration-300 hover:text-secondary">
          E-commerce Logo
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">Checkout</h1>
        <div className="w-24"></div> {/* Spacer for alignment */}
      </header>

      {/* Main Content */}
      <main className="flex-grow container mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left Column: Shipping & Payment Forms */}
        <div className="lg:col-span-1">
          <h2 className="text-3xl font-bold mb-6 text-gray-900">Checkout</h2>
          <p className="text-xl font-medium text-secondary mb-8">
            <span className="font-bold">Shipping</span> &gt; Payment &gt; Review
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            {/* Shipping Information */}
            <section className={`bg-white p-6 shadow-md ${borderRadiusClass}`}>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Shipping Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <Label htmlFor="fullName">Full Name</Label>
                  <Input id="fullName" type="text" placeholder="John Doe" {...register('fullName')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                  {errors.fullName && <p className="text-red-500 text-sm mt-1">{errors.fullName.message}</p>}
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="addressLine1">Address Line 1</Label>
                  <Input id="addressLine1" type="text" placeholder="123 Main St" {...register('addressLine1')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                  {errors.addressLine1 && <p className="text-red-500 text-sm mt-1">{errors.addressLine1.message}</p>}
                </div>
                <div>
                  <Label htmlFor="cityStateZip">City, State, Zip</Label>
                  <Input id="cityStateZip" type="text" placeholder="New York, NY 10001" {...register('cityStateZip')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                  {errors.cityStateZip && <p className="text-red-500 text-sm mt-1">{errors.cityStateZip.message}</p>}
                </div>
                <div>
                  <Label htmlFor="country">Country</Label>
                  <Input id="country" type="text" placeholder="United States" {...register('country')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                  {errors.country && <p className="text-red-500 text-sm mt-1">{errors.country.message}</p>}
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" type="tel" placeholder="(123) 456-7890" {...register('phone')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                  {errors.phone && <p className="text-red-500 text-sm mt-1">{errors.phone.message}</p>}
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="john.doe@example.com" {...register('email')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                  {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
                </div>
                <div className="flex items-center space-x-2 md:col-span-2 mt-2">
                  <Checkbox
                    id="useAsBillingAddress"
                    checked={watch('useAsBillingAddress')}
                    onCheckedChange={(checked) => setValue('useAsBillingAddress', checked as boolean)}
                    className="border-gray-300 data-[state=checked]:bg-secondary data-[state=checked]:text-white transition-all duration-300"
                  />
                  <Label htmlFor="useAsBillingAddress" className="text-base cursor-pointer">Use as Billing Address</Label>
                </div>
              </div>
            </section>

            {/* Shipping Method */}
            <section className={`bg-white p-6 shadow-md ${borderRadiusClass}`}>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Shipping Method</h3>
              <RadioGroup
                value={selectedShippingMethod}
                onValueChange={(value: 'standard' | 'express') => setValue('shippingMethod', value)}
                className="space-y-2"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="standard" id="standardShipping" className="border-gray-300 data-[state=checked]:border-secondary data-[state=checked]:text-secondary transition-all duration-300" />
                  <Label htmlFor="standardShipping" className="text-base cursor-pointer">Standard Shipping ($5.00)</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="express" id="expressShipping" className="border-gray-300 data-[state=checked]:border-secondary data-[state=checked]:text-secondary transition-all duration-300" />
                  <Label htmlFor="expressShipping" className="text-base cursor-pointer">Express Shipping ($15.00)</Label>
                </div>
              </RadioGroup>
              {errors.shippingMethod && <p className="text-red-500 text-sm mt-1">{errors.shippingMethod.message}</p>}
            </section>

            {/* Payment Method */}
            <section className={`bg-white p-6 shadow-md ${borderRadiusClass}`}>
              <h3 className="text-2xl font-semibold mb-6 text-gray-900">Payment Method</h3>
              <RadioGroup
                value={selectedPaymentMethod}
                onValueChange={(value: 'creditCard' | 'paypal') => setValue('paymentMethod', value)}
                className="flex space-x-6 mb-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="creditCard" id="creditCard" className="border-gray-300 data-[state=checked]:border-secondary data-[state=checked]:text-secondary transition-all duration-300" />
                  <Label htmlFor="creditCard" className="text-base cursor-pointer">Credit Card</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="paypal" id="paypal" className="border-gray-300 data-[state=checked]:border-secondary data-[state=checked]:text-secondary transition-all duration-300" />
                  <Label htmlFor="paypal" className="text-base cursor-pointer">PayPal</Label>
                </div>
              </RadioGroup>
              {errors.paymentMethod && <p className="text-red-500 text-sm mt-1">{errors.paymentMethod.message}</p>}

              {selectedPaymentMethod === 'creditCard' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 animate-fade-in">
                  <div className="md:col-span-2">
                    <Label htmlFor="cardNumber">Card Number</Label>
                    <Input id="cardNumber" type="text" placeholder="XXXX XXXX XXXX XXXX" {...register('cardNumber')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                    {errors.cardNumber && <p className="text-red-500 text-sm mt-1">{errors.cardNumber.message}</p>}
                  </div>
                  <div>
                    <Label htmlFor="expiryDate">Expiry Date</Label>
                    <Input id="expiryDate" type="text" placeholder="MM/YY" {...register('expiryDate')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                    {errors.expiryDate && <p className="text-red-500 text-sm mt-1">{errors.expiryDate.message}</p>}
                  </div>
                  <div>
                    <Label htmlFor="cvv">CVV</Label>
                    <Input id="cvv" type="text" placeholder="XXX" {...register('cvv')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                    {errors.cvv && <p className="text-red-500 text-sm mt-1">{errors.cvv.message}</p>}
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="cardholderName">Cardholder Name</Label>
                    <Input id="cardholderName" type="text" placeholder="John Doe" {...register('cardholderName')} className="h-10 border-gray-300 focus:border-secondary focus:ring-secondary transition-all duration-300" />
                    {errors.cardholderName && <p className="text-red-500 text-sm mt-1">{errors.cardholderName.message}</p>}
                  </div>
                </div>
              )}
            </section>
          </form> {/* Form ends here, but submit button is logically part of the form, placed outside for layout */}
        </div>

        {/* Right Column: Order Summary */}
        <div className="lg:col-span-1">
          <section className={`bg-white p-6 shadow-md ${borderRadiusClass} sticky top-8`}>
            <h3 className="text-2xl font-semibold mb-6 text-gray-900">Your Order</h3>
            <div className="space-y-3 mb-6">
              {mockCartItems.map((item) => (
                <p key={item.id} className="text-lg text-gray-700">
                  {item.name} x {item.quantity} @ ${item.price.toFixed(2)}
                </p>
              ))}
            </div>
            <div className="border-t border-gray-200 pt-4 space-y-2">
              <p className="flex justify-between text-lg text-gray-700">
                <span>Subtotal:</span>
                <span>${subtotal.toFixed(2)}</span>
              </p>
              <p className="flex justify-between text-lg text-gray-700">
                <span>Shipping:</span>
                <span>${shippingCost.toFixed(2)}</span>
              </p>
              <p className="flex justify-between text-lg text-gray-700">
                <span>Tax:</span>
                <span>${tax.toFixed(2)}</span>
              </p>
            </div>
            <div className="border-t border-gray-200 pt-4 mt-4">
              <p className="flex justify-between text-3xl font-bold text-gray-900">
                <span>TOTAL:</span>
                <span>${total.toFixed(2)}</span>
              </p>
            </div>

            <div className="flex items-center space-x-2 mt-8">
              <Checkbox
                id="agreeToTerms"
                checked={watch('agreeToTerms')}
                onCheckedChange={(checked) => setValue('agreeToTerms', checked as boolean)}
                className="border-gray-300 data-[state=checked]:bg-secondary data-[state=checked]:text-white transition-all duration-300"
              />
              <Label htmlFor="agreeToTerms" className="text-base cursor-pointer">I agree to Terms & Conditions</Label>
            </div>
            {errors.agreeToTerms && <p className="text-red-500 text-sm mt-1">{errors.agreeToTerms.message}</p>}

            <Button
              type="submit"
              onClick={handleSubmit(onSubmit)} // Attach submit handler to button
              className={`w-full mt-6 py-3 text-lg font-semibold text-white transition-all duration-300 ${borderRadiusClass}
                ${isLoading ? 'bg-secondary/70 cursor-not-allowed animate-pulse' : 'bg-secondary hover:bg-blue-600'}
              `}
              style={{ backgroundColor: secondaryColor, height: '48px' }}
              disabled={isLoading}
            >
              {isLoading ? 'Placing Order...' : 'PLACE ORDER'}
            </Button>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white shadow-inner py-6 px-6 flex justify-between items-center mt-8" style={{ height: '100px' }}>
        <p className="text-base text-gray-600">© 2023 E-commerce Site</p>
        <Link href="/privacy-policy" className="text-base text-gray-600 hover:text-secondary transition-colors duration-300">
          Privacy Policy
        </Link>
      </footer>
    </div>
  );
}