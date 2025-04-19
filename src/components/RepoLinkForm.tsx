import React, { useState } from 'react';
import { Github, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';

const RepoLinkForm: React.FC = () => {
  const [repoLink, setRepoLink] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoLink) return;
    
    // Simulate form submission
    setStatus('loading');
    
    // In a real app, this would be an API call
    setTimeout(() => {
      if (repoLink.includes('github.com')) {
        setStatus('success');
      } else {
        setStatus('error');
      }
    }, 1500);
  };
  
  return (
    <div className="w-full">
      <h2 className="text-space-star font-display text-2xl md:text-3xl font-bold mb-6">
        Enter Repository Link
      </h2>
      
      <form onSubmit={handleSubmit} className="w-full">
        <div className="relative">
          <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-space-accent">
            <Github size={20} />
          </div>
          
          <input
            type="text"
            value={repoLink}
            onChange={(e) => setRepoLink(e.target.value)}
            placeholder="https://github.com/username/repo"
            className={`
              w-full pl-12 pr-4 py-3 rounded-xl 
              bg-space-dark border-2 
              ${status === 'error' ? 'border-red-500' : 'border-space-accent/30'} 
              text-space-star placeholder:text-space-star/50
              focus:outline-none focus:border-space-accent
              transition-all duration-300
            `}
          />
          
          {status === 'loading' && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              <div className="w-5 h-5 border-2 border-space-accent border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
          
          {status === 'success' && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-green-500 animate-float">
              <CheckCircle size={20} />
            </div>
          )}
          
          {status === 'error' && (
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-red-500">
              <AlertCircle size={20} />
            </div>
          )}
        </div>
        
        <button
          type="submit"
          disabled={status === 'loading'}
          className={`
            mt-4 w-full flex items-center justify-center gap-2
            bg-gradient-to-r from-space-accent to-space-highlight 
            hover:from-space-highlight hover:to-space-accent
            text-white font-medium py-3 px-6 rounded-xl
            transition-all duration-300 transform hover:scale-[1.02]
            ${status === 'loading' ? 'opacity-70 cursor-not-allowed' : ''}
            shadow-lg shadow-space-accent/20 hover:shadow-space-accent/30
            animate-glow
          `}
        >
          <span>Generate Documentation</span>
          <ArrowRight size={18} />
        </button>
      </form>
      
      {status === 'error' && (
        <p className="mt-2 text-red-400 text-sm">
          Please enter a valid GitHub repository URL
        </p>
      )}
      
      <div className="mt-6 bg-space-dark/50 rounded-lg p-4 border border-space-accent/20">
        <h3 className="text-space-star font-display text-lg font-medium mb-2">
          Why Use Cosmic Documentation?
        </h3>
        <ul className="text-space-star/80 text-sm space-y-2">
          <li className="flex items-start gap-2">
            <div className="text-space-highlight mt-0.5">
              <CheckCircle size={16} />
            </div>
            <span>Beautiful, customizable readme templates</span>
          </li>
          <li className="flex items-start gap-2">
            <div className="text-space-highlight mt-0.5">
              <CheckCircle size={16} />
            </div>
            <span>Automatic code documentation generation</span>
          </li>
          <li className="flex items-start gap-2">
            <div className="text-space-highlight mt-0.5">
              <CheckCircle size={16} />
            </div>
            <span>Integration with GitHub workflows</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default RepoLinkForm;