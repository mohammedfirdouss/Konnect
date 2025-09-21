import type React from "react"
import { FiSearch, FiLock, FiTruck } from "react-icons/fi"
import ListItem from "./ui/ListItem"

const  HowItWorks =()=> {
  return (
    <section id="how-it-works" className="py-30 px-4 bg-background border-t border-[#1E1E1E]">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">How It Works</h2>
          <p className="md:text-lg text-[#B1B1B1]  max-w-2xl mx-auto">
            A simple 3-step flow designed for campus life. Discover listings, pay securely with escrow, and confirm delivery or service completion.
          </p>
        </div>

        <div className="space-y-3 w-full md:max-w-[80%] mx-auto">
          <ListItem
            color="bg-[#00FFA3]/30"
            icon={<FiSearch />}
            title="Discover"
            description="Browse goods, services, and student fundraisers near you."
          />
          <ListItem
                       color="bg-[#9945FF]/30"

            icon={<FiLock />}
            title="Pay with Escrow"
            description="Funds are held safely in escrow until both sides are satisfied."
          />
          <ListItem
          
            color="bg-[#00FFA3]/30"
                      

            icon={<FiTruck />}
            title="Deliver or Complete Service"
            description="Confirm delivery to release funds instantly on Solana."
          />
        </div>
      </div>
    </section>
  )
}


export default HowItWorks