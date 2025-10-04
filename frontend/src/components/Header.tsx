import Link from 'next/link'

interface HeaderProps {
  onChatOpen?: () => void;
}

export default function Header({ onChatOpen }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-8 py-6 flex items-center">
        <div className="flex items-center">
          <Link href="/" className="text-xl font-semibold text-gray-900">
            Veazy Logo
          </Link>
        </div>
        
        <div className="flex-1 flex items-center justify-end space-x-8">
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/how-it-works" className="text-gray-600 hover:text-gray-900 font-medium text-sm">
              How it Works
            </Link>
            <Link href="/about" className="text-gray-600 hover:text-gray-900 font-medium text-sm">
              About Us
            </Link>
          </nav>
          
          <div className="flex items-center space-x-4">
            <button 
              onClick={onChatOpen}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm"
            >
              ✨ Visa Genie
            </button>
            <button className="text-gray-600 hover:text-gray-900 font-medium text-sm">
              Sign Up ⚡
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}