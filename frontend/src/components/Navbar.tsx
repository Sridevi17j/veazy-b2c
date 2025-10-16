import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  onChatOpen?: () => void;
}

export const Navbar = ({ onChatOpen }: NavbarProps) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Globe className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">Veazy</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">
              Features
            </a>
            <a href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors">
              How It Works
            </a>
            <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors">
              Reviews
            </a>
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={onChatOpen}>
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};
