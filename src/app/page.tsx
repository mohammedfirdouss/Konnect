import { CoreFeatures } from "@/components/CoreFeature";
import  Footer  from "@/components/Footer";
import Header  from "@/components/Header";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import Showcase from "@/components/ShowCase";
import Verification from "@/components/Verification";


export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <HowItWorks />
        <CoreFeatures />
        <Showcase />
        <Verification />
      </main>
      <Footer />
    </div>
  )
}
