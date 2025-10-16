import { CheckCircle2, Clock, Timer } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const trackingSteps = [
  {
    title: "Documents verified",
    description: "All required documents are ready and validated",
    status: "complete",
    icon: CheckCircle2,
  },
  {
    title: "Application submitted",
    description: "Your application is being processed by the embassy",
    status: "progress",
    icon: Clock,
  },
  {
    title: "Visa approved",
    description: "Ready for your magical journey",
    status: "pending",
    icon: Timer,
  },
];

export const LiveTracking = () => {
  return (
    <section className="py-20 bg-background">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Watch Your Visa Application Live! ✨
          </h2>
        </div>

        <Card className="max-w-2xl mx-auto shadow-hover">
          <CardContent className="p-8">
            <div className="space-y-6">
              {trackingSteps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={index} className="flex gap-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                      step.status === 'complete' ? 'bg-success/10' :
                      step.status === 'progress' ? 'bg-primary/10' :
                      'bg-muted'
                    }`}>
                      <Icon className={`w-6 h-6 ${
                        step.status === 'complete' ? 'text-success' :
                        step.status === 'progress' ? 'text-primary' :
                        'text-muted-foreground'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold">{step.title}</h3>
                        <Badge variant={
                          step.status === 'complete' ? 'default' :
                          step.status === 'progress' ? 'secondary' :
                          'outline'
                        }>
                          {step.status === 'complete' ? '✓ Complete' :
                           step.status === 'progress' ? '⏳ In Progress' :
                           '⏱ Pending'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{step.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};
