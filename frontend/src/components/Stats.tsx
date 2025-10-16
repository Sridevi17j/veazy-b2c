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
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900">
            Why Travelers Love Veazy
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Join thousands of happy travelers who've discovered the magic of stress-free visa applications
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {benefits.map((benefit, index) => (
            <Card key={index} className="border-border hover:shadow-hover transition-all duration-300">
              <CardContent className="p-6">
                <div className="text-4xl md:text-5xl font-bold gradient-text mb-2">
                  {benefit.stat}
                </div>
                <h3 className="text-xl font-semibold mb-3">{benefit.label}</h3>
                <p className="text-sm text-muted-foreground">{benefit.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

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
