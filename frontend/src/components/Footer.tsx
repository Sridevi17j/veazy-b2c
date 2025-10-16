import { Globe } from "lucide-react";

export const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Globe className="h-6 w-6 text-blue-400" />
              <span className="text-lg font-bold">Veazy</span>
            </div>
            <p className="text-gray-400">Making visa applications magical for travelers worldwide.</p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <div className="space-y-2">
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Features</a>
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Pricing</a>
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Support</a>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <div className="space-y-2">
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">About</a>
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Blog</a>
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Careers</a>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <div className="space-y-2">
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Privacy</a>
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Terms</a>
              <a href="#" className="block text-gray-400 hover:text-white transition-colors">Security</a>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>© 2024 Veazy. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
