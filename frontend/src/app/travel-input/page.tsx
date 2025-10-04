export default function TravelInputPage() {
  return (
    <main className="min-h-screen bg-white">
      <section className="relative w-full h-screen">
        <div className="absolute" style={{ left: '1391px', top: '177px', width: '88px', height: '20px' }}>
          <span className="text-white font-bold text-base font-montserrat">Visa Genie</span>
        </div>

        <form className="absolute inset-0 flex items-center justify-center">
          <div className="grid grid-cols-4 gap-8 max-w-6xl w-full px-8">
            <div className="space-y-4">
              <label 
                className="block text-gray-800 font-medium text-base font-montserrat"
                style={{ color: '#282828' }}
              >
                Country
              </label>
              <input
                type="text"
                placeholder="Placeholder"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-montserrat"
                style={{ color: '#AFAFAF' }}
              />
            </div>

            <div className="space-y-4">
              <label 
                className="block text-gray-800 font-medium text-base font-montserrat"
                style={{ color: '#282828' }}
              >
                Date from
              </label>
              <input
                type="text"
                placeholder="Placeholder"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-montserrat"
                style={{ color: '#AFAFAF' }}
              />
            </div>

            <div className="space-y-4">
              <label 
                className="block text-gray-800 font-medium text-base font-montserrat"
                style={{ color: '#282828' }}
              >
                Date to
              </label>
              <input
                type="text"
                placeholder="Placeholder"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-montserrat"
                style={{ color: '#AFAFAF' }}
              />
            </div>

            <div className="space-y-4">
              <label 
                className="block text-gray-800 font-medium text-base font-montserrat"
                style={{ color: '#282828' }}
              >
                Purpose of Travel
              </label>
              <input
                type="text"
                placeholder="Placeholder"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-montserrat"
                style={{ color: '#AFAFAF' }}
              />
            </div>
          </div>
        </form>

        <div className="absolute bottom-16 left-1/2 transform -translate-x-1/2">
          <button 
            type="submit"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-bold text-base font-montserrat"
          >
            Continue
          </button>
        </div>

        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 max-w-4xl text-center">
          <p className="text-black font-semibold text-lg font-montserrat mb-4">
            Not sure about your visa type, required documents, or even how to plan your itinerary? Let Visa Genie handle it for you—get personalized guidance instantly.
          </p>
          <button className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors font-bold text-base font-montserrat">
            Ask Visa Genie
          </button>
        </div>
      </section>
    </main>
  )
}