import { MessageSquare, Globe2, Shield, Zap, Globe, FileText } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: MessageSquare,
    title: "Human-Like Conversations",
    description: "Chat naturally with our AI that understands context, nuance, and your unique travel situation.",
    gradient: "bg-gradient-to-r from-blue-500 to-cyan-500",
  },
  {
    icon: Globe2,
    title: "Smart Nationality Detection",
    description: "Our AI instantly knows your nationality, residence, and destination to provide precise visa information.",
    gradient: "bg-gradient-to-r from-purple-500 to-pink-500",
  },
  {
    icon: Shield,
    title: "Skip Government Sites",
    description: "Never navigate confusing government portals again. We handle all the bureaucracy for you.",
    gradient: "bg-gradient-to-r from-green-500 to-emerald-500",
  },
  {
    icon: Zap,
    title: "Real-Time Magic",
    description: "Watch your visa application progress live. See each step happening automatically in real-time.",
    gradient: "bg-gradient-to-r from-yellow-500 to-orange-500",
  },
  {
    icon: Globe,
    title: "Worldwide Coverage",
    description: "Supporting visa applications for 190+ countries with up-to-date requirements and processes.",
    gradient: "bg-gradient-to-r from-indigo-500 to-blue-500",
  },
  {
    icon: FileText,
    title: "Document Intelligence",
    description: "AI-powered document analysis ensures you have exactly what you need, nothing more or less.",
    gradient: "bg-gradient-to-r from-teal-500 to-green-500",
  },
];

export const Features = () => {
  return (
    <section id="features" className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Why Veazy is Pure Magic
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Experience the future of visa applications with AI that actually understands you
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="group hover:shadow-xl transition-all duration-300 border-0 shadow-lg hover:-translate-y-2">
                <CardContent className="p-6">
                  <div className={`w-12 h-12 rounded-lg ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2 text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600 text-base leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};
