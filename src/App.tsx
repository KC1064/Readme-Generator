import React, { useEffect } from 'react';
import Header from './components/Header';
import StarField from './components/StarField';
import SpaceIllustration from './components/SpaceIllustration';
import RepoLinkForm from './components/RepoLinkForm';

function App() {
  useEffect(() => {
    // Set document title
    document.title = 'Cosmic Dev | Space Repo Explorer';
  }, []);

  return (
    <div className="min-h-screen bg-space-gradient text-white relative overflow-hidden">
      {/* Animated star background */}
      <StarField />
      
      {/* Glow effects */}
      <div className="fixed top-1/4 left-1/4 w-96 h-96 rounded-full bg-space-purple opacity-10 blur-3xl"></div>
      <div className="fixed bottom-0 right-1/4 w-64 h-64 rounded-full bg-space-accent opacity-5 blur-3xl"></div>
      
      {/* Content */}
      <div className="relative z-10">
        <Header />
        
        <main className="container mx-auto px-4 py-8 md:py-16">
          <div className="flex flex-col lg:flex-row gap-8 md:gap-12 items-center">
            
            {/* Left column: Illustration */}
            <div className="w-full lg:w-1/2 h-[400px] md:h-[500px] rounded-2xl overflow-hidden shadow-xl shadow-space-accent/10 border border-space-accent/20 animate-float">
              <SpaceIllustration />
            </div>
            
            {/* Right column: Form */}
            <div className="w-full lg:w-1/2 bg-space-dark/80 backdrop-blur-lg p-6 md:p-8 rounded-2xl shadow-lg border border-space-accent/20">
              <RepoLinkForm />
            </div>
          </div>
          
          {/* Additional feature highlights or sections can be added here */}
        </main>
        
        <footer className="container mx-auto px-4 py-8 text-center text-space-star/50 text-sm">
          <p>© 2025 CosmicDev. Exploring the repository universe.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;