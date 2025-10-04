export default function VisaProcess() {
  return (
    <section className="py-12 bg-white">
      <div className="max-w-4xl mx-auto px-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-8">Visa approval process</h2>
        
        <div className="relative mb-12">
          <div className="absolute top-6 left-0 right-0 h-0.5 bg-purple-200"></div>
          
          <div className="grid grid-cols-3 gap-8 relative">
            <div className="text-center">
              <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-gray-600 mb-1">Step 1</h3>
                <h4 className="font-medium text-gray-900">Application Processing</h4>
              </div>
            </div>
            
            <div className="text-center">
              <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-gray-600 mb-1">Step 2</h3>
                <h4 className="font-medium text-gray-900">Approval Letter Issued</h4>
              </div>
            </div>
            
            <div className="text-center">
              <div className="w-6 h-6 bg-purple-600 rounded-full mx-auto mb-6 relative z-10"></div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-gray-600 mb-1">Step 3</h3>
                <h4 className="font-medium text-gray-900">Visa Stamping & Entry</h4>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Why it Works?</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>🚫 No agents, no hidden fees</li>
            <li>🤖 AI that knows embassy requirements inside-out.</li>
            <li>🇮🇳 Designed for Indian travellers, optimised for Vietnam.</li>
          </ul>
        </div>
      </div>
    </section>
  )
}