import { Card, CardContent } from "@/components/ui/card";
import { CheckCircle, Clock, Shield, Users, Zap, Heart } from "lucide-react";

const benefits = [
  {
    icon: CheckCircle,
    title: "Do It Yourself (But Not Really)",
    description: "Get the satisfaction of handling your own visa while our AI does all the heavy lifting behind the scenes.",
    stat: "100%",
    statLabel: "Success Rate"
  },
  {
    icon: Clock,
    title: "Save Hours of Confusion",
    description: "No more navigating confusing government websites or trying to decode complex visa requirements.",
    stat: "10x",
    statLabel: "Faster Process"
  },
  {
    icon: Shield,
    title: "Expert-Level Accuracy",
    description: "Our AI has processed thousands of visas and knows exactly what each country requires from your specific profile.",
    stat: "99.9%",
    statLabel: "Accuracy Rate"
  },
  {
    icon: Users,
    title: "Perfect for Groups",
    description: "Traveling with family or friends? Our AI handles multiple applicants and their unique requirements seamlessly.",
    stat: "50+",
    statLabel: "Group Applications"
  },
  {
    icon: Zap,
    title: "Real-Time Updates",
    description: "See your application progress live. No more wondering what's happening or when you'll hear back.",
    stat: "24/7",
    statLabel: "Live Tracking"
  },
  {
    icon: Heart,
    title: "Stress-Free Experience",
    description: "Travel planning should be exciting, not stressful. We remove all the visa anxiety so you can focus on your trip.",
    stat: "0",
    statLabel: "Stress Level"
  }
];

export const Benefits = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Why Travelers Love Veazy
          </h2>
          <p className="text-xl text-blue-100 max-w-3xl mx-auto">
            Join thousands of happy travelers who've discovered the magic of stress-free visa applications
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <Card key={index} className="bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2">
              <CardContent className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center">
                    <benefit.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">{benefit.stat}</div>
                    <div className="text-sm text-blue-200">{benefit.statLabel}</div>
                  </div>
                </div>
                
                <h3 className="text-xl font-semibold text-white mb-4">{benefit.title}</h3>
                <p className="text-blue-100 leading-relaxed">{benefit.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trust indicators */}
        <div className="mt-20 text-center">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <div className="text-3xl font-bold text-white mb-2">50K+</div>
              <div className="text-blue-200">Visas Processed</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">190+</div>
              <div className="text-blue-200">Countries Supported</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">4.9/5</div>
              <div className="text-blue-200">Customer Rating</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-2">24/7</div>
              <div className="text-blue-200">AI Support</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};