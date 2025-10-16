import { Card, CardContent } from "@/components/ui/card";
import { Quote, Star } from "lucide-react";

const testimonials = [
  {
    name: "Sarah Chen",
    location: "San Francisco, CA",
    avatar: "https://images.unsplash.com/photo-1649972904349-6e44c42644a7?w=60&h=60&fit=crop&crop=face",
    quote: "I was dreading the visa process for my Japan trip, but Veazy made it feel like magic! The AI understood exactly what I needed as a US citizen and handled everything. I literally watched my application progress in real-time - it was incredible!",
    destination: "Japan",
  },
  {
    name: "Marcus Rodriguez",
    location: "Madrid, Spain",
    avatar: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=60&h=60&fit=crop&crop=face",
    quote: "As a Spanish citizen planning a business trip to India, the visa requirements were overwhelming. The AI chat felt like talking to a real visa expert who knew my exact situation. Never touching a government website was the cherry on top!",
    destination: "India",
  },
  {
    name: "Emma Thompson",
    location: "London, UK",
    avatar: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=60&h=60&fit=crop&crop=face",
    quote: "Planning a family trip to Australia with three kids seemed impossible until I found Veazy. The AI handled all four of our applications simultaneously and kept me updated every step of the way. Pure magic indeed! ✨",
    destination: "Australia",
  },
];

export const Testimonials = () => {
  return (
    <section id="testimonials" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Real Stories from Happy Travelers
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            See how Veazy has transformed the visa experience for travelers worldwide
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="hover:shadow-xl transition-all duration-300 border-0 shadow-lg hover:-translate-y-2">
              <CardContent className="p-8">
                <div className="flex items-center mb-6">
                  <img 
                    src={testimonial.avatar} 
                    alt={testimonial.name} 
                    className="w-12 h-12 rounded-full object-cover mr-4"
                  />
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600">{testimonial.location}</p>
                  </div>
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                    ))}
                  </div>
                </div>
                
                <Quote className="w-8 h-8 text-blue-200 mb-4" />
                
                <blockquote className="text-gray-700 mb-6 leading-relaxed">
                  "{testimonial.quote}"
                </blockquote>
                
                <div className="flex items-center text-sm text-gray-500">
                  <span>Visa destination: </span>
                  <span className="ml-1 font-medium text-blue-600">{testimonial.destination}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Join the Magic! ✨</h3>
            <p className="text-gray-600 mb-6">Over 50,000 travelers have experienced the Veazy magic</p>
            <div className="flex justify-center items-center space-x-2">
              <div className="flex -space-x-2">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="w-10 h-10 bg-gradient-to-br from-blue-400 to-green-400 rounded-full border-2 border-white"></div>
                ))}
              </div>
              <span className="text-gray-600 ml-4">and thousands more...</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
