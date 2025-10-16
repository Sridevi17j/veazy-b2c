import { MessageSquare, Search, FileCheck, Plane } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const steps = [
  {
    number: "01",
    icon: MessageSquare,
    title: "Chat With Our AI",
    description: "Start a conversation about your travel plans. Our AI understands your nationality, destination, and travel purpose instantly.",
    color: "bg-blue-500",
  },
  {
    number: "02",
    icon: Search,
    title: "AI Finds Your Options",
    description: "Based on your profile, our AI identifies all available visa options, requirements, and the best path forward.",
    color: "bg-purple-500",
  },
  {
    number: "03",
    icon: FileCheck,
    title: "Documents & Application",
    description: "We guide you through document preparation and handle the entire government application process for you.",
    color: "bg-green-500",
  },
  {
    number: "04",
    icon: Plane,
    title: "Track & Travel",
    description: "Watch your application progress in real-time and get ready for your magical journey!",
    color: "bg-orange-500",
  },
];

const trackingSteps = [
  {
    title: "Documents verified",
    description: "All required documents are ready and validated",
    status: "complete",
    icon: FileCheck,
    bgColor: "bg-green-50",
    iconColor: "bg-green-500",
    textColor: "text-green-800",
    descColor: "text-green-600",
    statusText: "✓ Complete",
    statusColor: "text-green-600",
  },
  {
    title: "Application submitted",
    description: "Your application is being processed by the embassy",
    status: "progress",
    icon: Search,
    bgColor: "bg-blue-50",
    iconColor: "bg-blue-500 animate-pulse",
    textColor: "text-blue-800",
    descColor: "text-blue-600",
    statusText: "⏳ In Progress",
    statusColor: "text-blue-600",
  },
  {
    title: "Visa approved",
    description: "Ready for your magical journey",
    status: "pending",
    icon: Plane,
    bgColor: "bg-gray-50 opacity-50",
    iconColor: "bg-gray-400",
    textColor: "text-gray-600",
    descColor: "text-gray-500",
    statusText: "⏱ Pending",
    statusColor: "text-gray-500",
  },
];

export const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            How the Magic Happens
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Four simple steps to visa freedom. No government sites, no confusion, just pure magic.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={index} className="relative">
                {/* Connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-gray-300 to-transparent transform translate-x-4 z-0"></div>
                )}
                
                <Card className="relative z-10 h-full hover:shadow-xl transition-all duration-300 border-0 shadow-md hover:-translate-y-2">
                  <CardContent className="p-8 text-center">
                    <div className={`w-16 h-16 ${step.color} rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <div className="text-3xl font-bold text-gray-300 mb-2">
                      {step.number}
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">{step.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{step.description}</p>
                  </CardContent>
                </Card>
              </div>
            );
          })}
        </div>

        {/* Live Tracking Section */}
        <div className="mt-20 bg-white rounded-2xl shadow-xl p-8 mx-auto max-w-4xl">
          <h3 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Watch Your Visa Application Live! ✨
          </h3>
          <div className="space-y-4">
            {trackingSteps.map((step, index) => {
              const Icon = step.icon;
              return (
                <div key={index} className={`flex items-center space-x-4 p-4 ${step.bgColor} rounded-lg`}>
                  <div className={`w-8 h-8 ${step.iconColor} rounded-full flex items-center justify-center`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className={`font-medium ${step.textColor}`}>{step.title}</p>
                    <p className={`text-sm ${step.descColor}`}>{step.description}</p>
                  </div>
                  <div className={`${step.statusColor} font-medium`}>{step.statusText}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
