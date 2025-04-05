interface PageBackgroundProps {
  children: React.ReactNode;
}

export default function PageBackground({ children }: PageBackgroundProps) {
  return (
    <div className="relative min-h-screen">
      <div 
        className="absolute inset-0 w-full bg-no-repeat bg-cover bg-center"
        style={{ backgroundImage: 'url("/page-bg.png")' }}
      />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
} 