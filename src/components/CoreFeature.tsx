import type React from "react"
import { FiShoppingBag, FiShield, FiUsers, FiZap } from "react-icons/fi"
import ListItem from "./ui/ListItem"

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
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

export function CoreFeatures() {
  return (
    <section id="features" className="py-30 px-4 border-t border-[#1B1B1B] bg-[#1E1E1E]">
      <div className="container mx-auto w-full">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">Core Features</h2>
          <p className="md:text-lg text-[#B1B1B1] max-w-2xl mx-auto">
            Everything you need to power campus commerce with speed, trust, and transparency.
          </p>
        </div>

        <div className="space-y-6 w-full md:max-w-[80%] mx-auto">
      
                  
                  <ListItem
                       color="bg-[#00FFA3]/30"
                       icon={<FiShoppingBag />}
                       title="Marketplace for Goods & Services"
                       description="List, discover, and transact on a campus-first marketplace built for students."
          />
                  <ListItem
                       color="bg-[#00FFA3]/30"
                      
            icon={<FiShield />}
            title="Escrow-Secured Payments"
            description="Pay in SOL or stablecoins with clear escrow status at every step."
          />
                  <ListItem
                       color="bg-[#00FFA3]/30"
                      
            icon={<FiUsers />}
            title="Student Crowdfunding Hub"
            description="Transparent progress bars and verified causes for clubs and teams."
          />
                  <ListItem
                       color="bg-[#00FFA3]/30"
                      
            icon={<FiZap />}
            title="AI-Powered Recommendations"
            description="Smart suggestions and fraud detection to keep your campus safe."
          />
        </div>
      </div>
    </section>
  )
}
