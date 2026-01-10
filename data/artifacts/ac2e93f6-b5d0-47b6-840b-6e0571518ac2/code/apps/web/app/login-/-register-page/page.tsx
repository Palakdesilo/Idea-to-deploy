"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2, Facebook, Google } from 'lucide-react';
import { api } from '@/lib/api'; // Assuming this utility exists

// Design Tokens
const primaryColor = '#0f172a'; // slate-900
const secondaryColor = '#3b82f6'; // blue-500
const borderRadius = '1rem'; // rounded-xl

// Zod Schemas
const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean().optional(),
});

const registerSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirmPassword: z.string().min(6, 'Confirm password is required'),
  subscribeNewsletter: z.boolean().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type LoginFormInputs = z.infer<typeof loginSchema>;
type RegisterFormInputs = z.infer<typeof registerSchema>;

// Reusable Input Component
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  id: string;
  error?: string;
}

const Input: React.FC<InputProps> = ({ label, id, error, type = 'text', ...props }) => (
  <div className="mb-4">
    <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
      {label}
    </label>
    <input
      id={id}
      type={type}
      className={`w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-200 ${
        error ? 'border-red-500' : ''
      }`}
      style={{ borderRadius: borderRadius }}
      {...props}
    />
    {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
  </div>
);

// Reusable Checkbox Component
interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  id: string;
}

const Checkbox: React.FC<CheckboxProps> = ({ label, id, ...props }) => (
  <div className="flex items-center mb-4">
    <input
      id={id}
      type="checkbox"
      className="h-4 w-4 text-secondary border-gray-300 rounded focus:ring-secondary"
      {...props}
    />
    <label htmlFor={id} className="ml-2 block text-sm text-gray-700 cursor-pointer">
      {label}
    </label>
  </div>
);

// Reusable Button Component
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary', loading, ...props }) => {
  const baseClasses = `flex items-center justify-center font-semibold py-2 px-4 rounded-xl transition-all duration-300 animate-fade-in`;
  const primaryClasses = `bg-secondary text-white hover:opacity-90 shadow-md`;
  const secondaryClasses = `bg-gray-200 text-primary hover:bg-gray-300`;
  const outlineClasses = `border border-secondary text-secondary hover:bg-secondary hover:text-white`;

  let classes = baseClasses;
  if (variant === 'primary') classes += ` ${primaryClasses}`;
  if (variant === 'secondary') classes += ` ${secondaryClasses}`;
  if (variant === 'outline') classes += ` ${outlineClasses}`;

  return (
    <button
      className={classes}
      style={{ borderRadius: borderRadius }}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
};

const LoginRegisterPage: React.FC = () => {
  const router = useRouter();
  const [loginLoading, setLoginLoading] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [registerError, setRegisterError] = useState<string | null>(null);

  const {
    register: registerLogin,
    handleSubmit: handleLoginSubmit,
    formState: { errors: loginErrors },
  } = useForm<LoginFormInputs>({
    resolver: zodResolver(loginSchema),
  });

  const {
    register: registerRegister,
    handleSubmit: handleRegisterSubmit,
    formState: { errors: registerErrors },
  } = useForm<RegisterFormInputs>({
    resolver: zodResolver(registerSchema),
  });

  const onLogin = async (data: LoginFormInputs) => {
    setLoginLoading(true);
    setLoginError(null);
    try {
      const response = await api.post('/auth/login', {
        email: data.email,
        password: data.password,
      });
      localStorage.setItem('authToken', response.data.token);
      router.push('/homepage'); // Redirect to homepage on success
    } catch (error: any) {
      setLoginError(error.response?.data?.message || 'Login failed. Please try again.');
    } finally {
      setLoginLoading(false);
    }
  };

  const onRegister = async (data: RegisterFormInputs) => {
    setRegisterLoading(true);
    setRegisterError(null);
    try {
      const response = await api.post('/auth/register', {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        password: data.password,
      });
      localStorage.setItem('authToken', response.data.token);
      router.push('/homepage'); // Redirect to homepage on success
    } catch (error: any) {
      setRegisterError(error.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setRegisterLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="h-20 bg-white shadow-sm flex items-center justify-between px-6 md:px-12" style={{ backgroundColor: 'white' }}>
        <Link href="/homepage" className="text-xl font-bold" style={{ color: primaryColor }}>
          E-commerce Site
        </Link>
        <div className="text-base font-medium" style={{ color: primaryColor }}>
          My Account
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col md:flex-row justify-center items-start py-8 px-6 md:px-12 lg:px-24 xl:px-32">
        <h1 className="text-3xl font-bold mb-8 md:hidden w-full text-center" style={{ color: primaryColor }}>
          Login / Register
        </h1>

        {/* Login Section */}
        <section
          className="w-full md:w-1/2 lg:w-2/5 xl:w-1/3 p-8 bg-white rounded-xl shadow-lg animate-fade-in mb-8 md:mb-0"
          style={{ borderRadius: borderRadius }}
        >
          <h2 className="text-2xl font-semibold mb-6" style={{ color: primaryColor }}>
            Login
          </h2>
          <form onSubmit={handleLoginSubmit(onLogin)}>
            <Input
              id="login-email"
              label="Email Address"
              type="email"
              {...registerLogin('email')}
              error={loginErrors.email?.message}
            />
            <Input
              id="login-password"
              label="Password"
              type="password"
              {...registerLogin('password')}
              error={loginErrors.password?.message}
            />
            <div className="flex items-center justify-between mb-6">
              <Checkbox
                id="remember-me"
                label="Remember Me"
                {...registerLogin('rememberMe')}
              />
              <Link href="#" className="text-sm text-secondary hover:underline transition-all duration-200">
                Forgot Password?
              </Link>
            </div>
            {loginError && <p className="text-red-500 text-sm mb-4">{loginError}</p>}
            <Button type="submit" loading={loginLoading} className="w-full h-10">
              LOGIN
            </Button>
          </form>

          <div className="flex items-center my-6">
            <hr className="flex-grow border-gray-300" />
            <span className="px-3 text-gray-500 text-sm">OR</span>
            <hr className="flex-grow border-gray-300" />
          </div>

          <Button variant="secondary" className="w-full mb-4 h-10" onClick={() => alert('Google Login')}>
            <Google className="mr-2 h-5 w-5" /> Login with Google
          </Button>
          <Button variant="secondary" className="w-full h-10" onClick={() => alert('Facebook Login')}>
            <Facebook className="mr-2 h-5 w-5" /> Login with Facebook
          </Button>
        </section>

        {/* Register Section */}
        <section
          className="w-full md:w-1/2 lg:w-2/5 xl:w-1/3 p-8 bg-white rounded-xl shadow-lg animate-fade-in md:ml-8"
          style={{ borderRadius: borderRadius }}
        >
          <h2 className="text-2xl font-semibold mb-6" style={{ color: primaryColor }}>
            Create an Account
          </h2>
          <form onSubmit={handleRegisterSubmit(onRegister)}>
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  id="register-firstName"
                  label="First Name"
                  {...registerRegister('firstName')}
                  error={registerErrors.firstName?.message}
                />
              </div>
              <div className="flex-1">
                <Input
                  id="register-lastName"
                  label="Last Name"
                  {...registerRegister('lastName')}
                  error={registerErrors.lastName?.message}
                />
              </div>
            </div>
            <Input
              id="register-email"
              label="Email Address"
              type="email"
              {...registerRegister('email')}
              error={registerErrors.email?.message}
            />
            <Input
              id="register-password"
              label="Password"
              type="password"
              {...registerRegister('password')}
              error={registerErrors.password?.message}
            />
            <Input
              id="register-confirmPassword"
              label="Confirm Password"
              type="password"
              {...registerRegister('confirmPassword')}
              error={registerErrors.confirmPassword?.message}
            />
            <Checkbox
              id="subscribe-newsletter"
              label="Subscribe to Newsletter"
              {...registerRegister('subscribeNewsletter')}
            />
            {registerError && <p className="text-red-500 text-sm mb-4">{registerError}</p>}
            <Button type="submit" loading={registerLoading} className="w-full h-10">
              REGISTER
            </Button>
          </form>
        </section>
      </main>

      {/* Footer */}
      <footer className="h-24 flex flex-col md:flex-row items-center justify-between px-6 md:px-12 py-4 text-white" style={{ backgroundColor: primaryColor }}>
        <p className="text-sm mb-2 md:mb-0">© 2023 E-commerce Site</p>
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm mb-2 md:mb-0">
          <Link href="#" className="hover:underline">About Us</Link>
          <Link href="#" className="hover:underline">Contact</Link>
          <Link href="#" className="hover:underline">FAQ</Link>
          <Link href="#" className="hover:underline">Privacy</Link>
        </div>
        <div className="flex items-center gap-4 mb-2 md:mb-0">
          {/* Placeholder for Social Icons */}
          <span className="text-sm">Social Icons</span>
        </div>
        <div className="flex items-center">
          <input
            type="email"
            placeholder="Email for Newsletter"
            className="p-2 text-sm rounded-l-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent transition-all duration-200"
            style={{ borderRadius: `${borderRadius} 0 0 ${borderRadius}` }}
          />
          <Button className="h-auto py-2 px-3 text-sm rounded-r-md" style={{ borderRadius: `0 ${borderRadius} ${borderRadius} 0` }}>
            Subscribe
          </Button>
        </div>
      </footer>
    </div>
  );
};

export default LoginRegisterPage;