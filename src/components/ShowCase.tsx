interface ScreenshotItem {
  title: string
  image: string
  colSpan?: number
  aspectRatio?: string
}

const Showcase =()=> {
    const screenshots: ScreenshotItem[] = [
      {
        title: "Onboarding & Wallet Setup",
        image: "/images/sol.jpg",
        aspectRatio: "aspect-[3/4]"
      },
      {
        title: "Marketplace",
        image: "/images/laptop.jpg",
        aspectRatio: "aspect-[3/4]"
      },
      {
        title: "Product Detail",
        image: "/images/mockup-free.jpg",
        aspectRatio: "aspect-[2/1]"
      },
      {
        title: "Payments & Escrow",
        image: "/images/scan.jpg",
        aspectRatio: "aspect-[3/4]"
      },
      {
        title: "Crowdfunding",
        image: "/images/coins.png",
        aspectRatio: "aspect-[2/1]"
      },
      {
        title: "Seller Dashboard",
        image: "/images/analytics.jpg",
        aspectRatio: "aspect-[3/4]"
      },
      {
        title: "Profile & Verification",
        image: "/images/wallet.jpg",
        aspectRatio: "aspect-[3/4]"
      },
      {
        title: "AI Recommendations",
          image: "/images/apps.jpg",
        aspectRatio: "aspect-[3/4]"
      },
    ]

    const ScreenshotCard = ({ item, index }: { item: ScreenshotItem, index: number }) => (
      <div 
        className="bg-[#1E1E1E] rounded-xl overflow-hidden  border border-border/50 mb-3 shadow-lg">
        <div className="h-[300px] md:h-[350px]">
          <img
            src={item.image}
            alt={item.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
        <p className="text-sm md:text-base text-white/80 font-medium p-[8px] md:p-[12px]">{item.title}</p>
      </div>
    )
  
    return (
      <section className="py-30 px-4 bg-muted/20">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">Screenshots Showcase</h2>
            <p className="md:text-lg text-[#B1B1B1] ">A peek at the Konnect app experience.</p>
          </div>
  
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-[18px]  max-w-6xl mx-auto">
            {screenshots.map((item, index) => (
              <ScreenshotCard key={index} item={item} index={index} />
            ))}
          </div>
        </div>
      </section>
    )
  }
  

  export default Showcase