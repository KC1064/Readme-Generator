import React from 'react';
import { Github, Rocket } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="w-full py-4 px-6 md:px-8 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <Rocket 
          size={32} 
          className="text-space-highlight animate-float" 
          strokeWidth={1.5} 
        />
        <h1 className="text-space-star font-display text-xl md:text-2xl font-bold tracking-wider">
          COSMIC<span className="text-space-accent">DEV</span>
        </h1>
      </div>
      
      <a 
        href="https://github.com" 
        target="_blank" 
        rel="noopener noreferrer"
        className="p-2 rounded-full bg-space-mid text-space-star hover:bg-space-accent transition-colors duration-300 flex items-center justify-center"
        aria-label="GitHub"
      >
        <Github size={24} strokeWidth={1.5} />
      </a>
    </header>
  );
};

export default Header;