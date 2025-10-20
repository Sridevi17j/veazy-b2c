import { Card, CardContent } from "@/components/ui/card";

const benefits = [
  { stat: "100%", label: "Success Rate", description: "Get the satisfaction of handling your own visa while our AI does all the heavy lifting behind the scenes." },
  { stat: "10x", label: "Faster Process", description: "No more navigating confusing government websites or trying to decode complex visa requirements." },
  { stat: "99.9%", label: "Accuracy Rate", description: "Our AI has processed thousands of visas and knows exactly what each country requires from your specific profile." },
  { stat: "50+", label: "Group Applications", description: "Traveling with family or friends? Our AI handles multiple applicants and their unique requirements seamlessly." },
  { stat: "24/7", label: "Live Tracking", description: "See your application progress live. No more wondering what's happening or when you'll hear back." },
  { stat: "0", label: "Stress Level", description: "Travel planning should be exciting, not stressful. We remove all the visa anxiety so you can focus on your trip." },
];

const quickStats = [
  { number: "50K+", label: "Visas Processed" },
  { number: "190+", label: "Countries Supported" },
  { number: "4.9/5", label: "Customer Rating" },
  { number: "24/7", label: "AI Support" },
];

export const Stats = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-blue-600/15 via-purple-600/10 to-green-600/15 relative overflow-hidden">
      {/* Background overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-accent/5"></div>
      
      <div className="container mx-auto px-4 relative z-10">

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {quickStats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-primary mb-2">
                {stat.number}
              </div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
