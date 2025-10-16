import { ArrowRight, MessageCircle, Sparkles, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface CTAProps {
  onChatOpen?: () => void;
}

export const CTA = ({ onChatOpen }: CTAProps) => {
  return (
    <section className="py-20 bg-gradient-to-br from-blue-400 via-purple-400 to-green-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="bg-white/10 backdrop-blur-sm border-white/20 shadow-2xl">
          <CardContent className="p-12 text-center">
            <div className="mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-full mb-6">
                <Globe className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">Ready for Visa Magic?</h2>
              <p className="text-xl text-gray-700 max-w-3xl mx-auto mb-8">
                Stop struggling with government websites and confusing visa requirements. Let our AI handle everything while you focus on planning your amazing trip! ✈️
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-8">
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600 text-lg px-8 py-4 font-semibold"
                onClick={onChatOpen}
              >
                <MessageCircle className="w-5 h-5 mr-2" />
                Start Your Visa Journey
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="bg-gradient-to-r from-purple-500 to-green-500 text-white hover:from-purple-600 hover:to-green-600 border-0 text-lg px-8 py-4"
                onClick={onChatOpen}
              >
                <Sparkles className="w-5 h-5 mr-2" />
                See a Demo
              </Button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl mx-auto text-gray-700">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm">Free consultation</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm">No hidden fees</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm">Money-back guarantee</span>
              </div>
            </div>

            <div className="mt-12 pt-8 border-t border-gray-300">
              <p className="text-gray-600 text-sm mb-4">Trusted by travelers worldwide</p>
              <div className="flex justify-center items-center space-x-8 opacity-80">
                <div className="text-gray-700 font-medium">190+ Countries</div>
                <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
                <div className="text-gray-700 font-medium">50K+ Visas</div>
                <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
                <div className="text-gray-700 font-medium">24/7 Support</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};
