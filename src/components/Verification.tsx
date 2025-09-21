import type React from "react"
import { FiShield, FiLock, FiBarChart } from "react-icons/fi"
import ListItem from "./ui/ListItem"

interface TrustFeatureProps {
  icon: React.ReactNode
  title: string
  description: string
}

function TrustFeature({ icon, title, description }: TrustFeatureProps) {
  return (
    <div className="flex items-start space-x-4 p-6 rounded-lg border border-border/50 bg-card/30 hover:bg-card/50 transition-colors">
      <div className="w-12 h-12 bg-secondary/20 rounded-lg flex items-center justify-center flex-shrink-0">
        <div className="text-secondary text-xl">{icon}</div>
      </div>
      <div>
        <h3 className="text-lg font-semibold mb-2 text-white">{title}</h3>
        <p className="text-white/80">{description}</p>
      </div>
    </div>
  )
}

const Verification =()=> {
  return (
    <section id="trust" className="py-30 px-4 bg-[#1E1E1E]">
      <div className="container mx-auto w-full">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">Trust & Verification</h2>
          <p className="md:text-lg text-[#B1B1B1]  max-w-2xl mx-auto">Fintech-grade safety built for students.</p>
        </div>

             
        <div className="space-y-3 w-full md:max-w-[80%] mx-auto">
                  
     
                  
                  <ListItem
                       color="bg-[#9945FF]/30"

                       icon={<FiShield />}
                       title="NFT Badge System"
                       description="Earn and display verifiable NFT badges for trusted sellers and fundraisers."
          />
          <ListItem
                      icon={<FiLock />}
            color="bg-[#00FFA3]/30"
                
                      
            title="Escrow Protection"
            description="Funds are released only when the buyer confirms delivery or service completion."
          />
          <ListItem
                      icon={<FiBarChart />}
                      color="bg-[#9945FF]/30"
                      
            title="Transparent Donations"
            description="Clear tracking for contributions, goals, and progress across campus campaigns."
          />
        </div>
      </div>
    </section>
  )
}

export default Verification
