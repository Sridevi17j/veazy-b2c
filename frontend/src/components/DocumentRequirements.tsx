export default function DocumentRequirements() {
  return (
    <section className="py-12 bg-white">
      <div className="max-w-4xl mx-auto px-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-8">Documents Requirement for Thailand</h2>
        
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-3 text-gray-900">Passport</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  A valid passport with a minimum of 6 months&apos; validity from the date of return. 
                  Ensure at least 2 blank pages for visa stamping.
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-start space-x-4">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold mb-3 text-gray-900">Flight Tickets</h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  Round-trip flight tickets showing entry and exit from the country. Dummy 
                  tickets are accepted in some cases.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}