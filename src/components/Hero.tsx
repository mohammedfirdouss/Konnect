import Button  from "@/components/ui/Button"
import  Badge  from "@/components/ui/Badge"
import Image from "next/image"

const Hero = () => {
    

    const features =[
        {
            title: "Markteplace",
            tag: "Escrow",
            icon: "",
            image: "/images/shopping.jpg"
            
        },
        {
            title: "Crowdfunding",
            tag: "Verified",
            icon:"",
            image:"/images/atm.jpg"
            
        },
    ]
  return (
    <section className="py-20 px-4">
      <div className="container mx-auto text-center">
        <Badge  className="mb-10 bg-[#9945FF]/60 text-white rounded-[100px] border-secondary/50 px-4 py-2 text-sm font-medium">
          Built on Solana
        </Badge>

        <h1 className="text-3xl md:text-6xl font-bold mb-3 text-balance text-white">Campus Commerce Powered by Solana.</h1>

        <p className="md:text-xl text-[#B1B1B1] mb-10 max-w-5xl mx-auto">
          Konnect is the mobile-first marketplace and payment platform for students. Buy, sell, and fund projects with escrow-secured payments in SOL and stablecoins.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Button size="sm" className="w-fit mx-auto !text-sm" variant="konnect">
          Download App
          </Button>
          {/* <Button size="lg" variant="outline" className="border-white/20 text-white hover:bg-white/10 bg-[#1E1E1E]">
            Download App
          </Button> */}
        </div>

              <div className="w-full grid grid-cols-1 md:grid-cols-2 md:p-[20px] gap-[20px]  max-w-6xl mx-auto md:bg-[#1E1E1E] rounded-[20px]">
                  
                  {features.map((e) => (
                      <div className="flex flex-col items-center w-full rounded-[20px] p-[20px] bg-[#1E1E1E] border border-[#1E1E1E] lg:w-auto" key={e.title}>
                      <div className="flex items-center justify-between w-full gap-2 mb-4">
                              <h3 className="text-sm md:text-lg font-semibold text-white">{e.title }</h3>
                        <Badge className="bg-[#9945FF]/30 text-secondary rounded-[100px] border-secondary/50 px-3 py-1 text-xs font-medium">
                          {e.tag}
                        </Badge>
                      </div>
                      <div className="relative w-full h-[300px] md:h-[400px]">
                        <img src={e.image} alt={e.title} width={100} height={100} className="w-full h-full rounded-[20px] object-cover" />
                      </div>
                    </div>
           
                  ))}
         
       
        </div>
      </div>
    </section>
  )
    
}

export default Hero
