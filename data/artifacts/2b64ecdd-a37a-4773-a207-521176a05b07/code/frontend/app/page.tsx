export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <nav className="flex justify-between items-center p-6 max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-blue-600">App</h1>
        <div className="space-x-4">
          <a href="/login" className="px-4 py-2 text-gray-700 hover:text-blue-600">Login</a>
          <a href="/register" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Get Started</a>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-20 text-center">
        <h2 className="text-5xl font-bold text-gray-900 mb-6">CREATE A SOCIAL MEDIA PLATFORM
</h2>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Welcome to your application. Get started by exploring the features.
        </p>
        <div className="flex gap-4 justify-center">
          <a href="/register" className="px-8 py-3 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700">
            Get Started
          </a>
          <a href="/dashboard" className="px-8 py-3 border-2 border-blue-600 text-blue-600 rounded-lg text-lg font-semibold hover:bg-blue-50">
            Learn More
          </a>
        </div>
      </main>
    </div>
  );
}