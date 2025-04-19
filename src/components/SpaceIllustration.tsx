import React from 'react';

const SpaceIllustration: React.FC = () => {
  return (
    <div className="relative w-full h-full flex items-center justify-center overflow-hidden rounded-2xl bg-space-mid p-4">
      <div className="absolute inset-0 bg-nebula opacity-70"></div>
      
      {/* Planet */}
      <div className="relative w-48 h-48 rounded-full bg-gradient-to-br from-space-purple to-space-accent animate-pulse-slow">
        <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-transparent via-transparent to-space-highlight opacity-30"></div>
        
        {/* Rings */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-16 border-4 border-space-highlight opacity-20 rounded-full rotate-12"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-16 border-2 border-space-star opacity-10 rounded-full rotate-12"></div>
        
        {/* Orbiting moon */}
        <div className="absolute -top-4 -right-4 w-12 h-12 rounded-full bg-space-star opacity-80 shadow-lg animate-float"></div>
        
        {/* Surface details */}
        <div className="absolute top-1/4 left-1/4 w-12 h-8 rounded-full bg-space-purple opacity-40"></div>
        <div className="absolute bottom-1/3 right-1/4 w-16 h-10 rounded-full bg-space-pink opacity-30"></div>
      </div>
      
      {/* Floating text */}
      <div className="absolute bottom-8 left-0 right-0 text-center">
        <h2 className="text-space-star font-display text-xl md:text-2xl font-medium tracking-wide">
          Explore the Repository Universe
        </h2>
        <p className="text-space-star/70 text-sm mt-2 max-w-md mx-auto">
          Generate beautiful documentation and readme files for your cosmic code
        </p>
      </div>
    </div>
  );
};

export default SpaceIllustration;