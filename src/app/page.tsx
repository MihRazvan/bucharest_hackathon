import Image from 'next/image';

export default function Home() {
  return (
    <div className="w-screen -mx-[calc((100vw-100%)/2)] -mt-[1px]">
      <a href="/company" className="block">
        <Image
          src="/landing.png"
          alt="Pipe It Landing Page"
          width={1920}
          height={1080}
          className="w-screen h-auto"
          quality={100}
          priority
        />
      </a>
    </div>
  );
}
